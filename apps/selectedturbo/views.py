import math
import json

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from .services.project import Project
from .services.design_points import RatedPoint, DutyPoint
from .services.base_points import BasePoint
from .services.turbo_data import TurboData
from .services.const import ORDEN, DO_OIL, CONTROL_PANEL, PLATE_SURFACE_TEMP, TEMP_RISE_AE, UAIR_MAX, \
MAX_FLOW_COEFF, PRESSURE_COEFF
from .models import Turbo, TestPoints
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SelectionForm


def print_attributes(obj):
    for x, y in obj.__dict__.items():
        print("%s:%s" % (x,y))
    print("\n")


def initial_turbo_list():
    type_list = ["GL1", "GL2", "GL3", "GL5", "GL8", "GL10", "GL15", "GL20", "GL30", "GL50"]
    turbo_list = []

    for type in type_list:
        turbos = Turbo.objects.filter(category=type).order_by("cut_back")[:4]
        # TODO 判断种类以及数量
        for turbo in turbos:
            turbo_data = TurboData(turbo)
            turbo_list.append(turbo_data)

    return turbo_list


def get_all_base_points(category="GL3"):
    base_points_collection = []
    for x in range(1, 12):
        condition_collection = []
        for y in range (1, 9):
            point_set = TestPoints.objects.filter(working_condition=x, working_position=y)[:1]
            for point in point_set:
                base_point = BasePoint(point)
                condition_collection.append(base_point)
        base_points_collection.append(condition_collection)
    return base_points_collection


def single_triangle_calculation(base_point_a, base_point_b, base_point_c, design_point_d):
    ab = ((base_point_a.flow_coef - base_point_b.flow_coef)**2 + (base_point_a.pressure_coef - base_point_b.pressure_coef)**2)**0.5
    bc = ((base_point_b.flow_coef - base_point_c.flow_coef)**2 + (base_point_b.pressure_coef - base_point_c.pressure_coef)**2)**0.5
    ac = ((base_point_a.flow_coef - base_point_c.flow_coef)**2 + (base_point_a.pressure_coef - base_point_c.pressure_coef)**2)**0.5

    angle_bac = angle_b(ab, bc, ac)
    area_abc = area(ab, ac, angle_bac)

    da = ((base_point_a.flow_coef - design_point_d.phi)**2 + (base_point_a.pressure_coef - design_point_d.psi)**2)**0.5
    db = ((base_point_b.flow_coef - design_point_d.phi)**2 + (base_point_b.pressure_coef - design_point_d.psi)**2)**0.5
    dc = ((base_point_c.flow_coef - design_point_d.phi)**2 + (base_point_c.pressure_coef - design_point_d.psi)**2)**0.5

    angle_bad = angle_b(ab, db, da)
    angle_dac = angle_b(ac, dc, da)
    angle_bdc = angle_b(db, bc, dc)

    area_abd = area(ab, da, angle_bad)
    area_dac = area(ac, da, angle_dac)
    area_dbc = area(db, dc, angle_bdc)

    area_sum = area_abd + area_dac + area_dbc

    area_ratio = area_abc / area_sum

    eff_interpolation = 0.0

    if area_ratio > 0.999:
        eff_interpolation = (base_point_a.efficiency * area_dbc + base_point_b.efficiency * area_dac
                            + base_point_c.efficiency * area_abd) / area_abc

    return eff_interpolation, area_ratio


def angle_b(a, b, c):
    return math.acos((a**2 + c**2 - b**2) / (2 * a * c) )


def area(a, c, angle):
    return 0.5 * math.sin(angle) * a * c


def rated_point_interpolation(rated_point, duty_points_collect, base_points_collect):
    eff_sum = 0.0
    for x in range(0, 10):
        for y in range(0, 7):
            base_point_a = base_points_collect[x][y+1]
            base_point_b = base_points_collect[x+1][y]
            base_points_c = base_points_collect[x][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, rated_point)
            eff_sum += eff

        for y in range(0, 7):
            base_point_a = base_points_collect[x][y+1]
            base_point_b = base_points_collect[x+1][y+1]
            base_points_c = base_points_collect[x+1][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, rated_point)
            eff_sum += eff

    if eff_sum == 0.0:
        eff_sum = 0.74
    elif eff_sum > 1:
        eff_sum /= 2

    rated_point.update_data_relt_to_efficiency(eff_sum)
    for x in duty_points_collect:
        for y in x:
            y.update_data_relt_to_rated_point(rated_point)


def duty_point_interpolation(duty_point, rated_point, base_points_collect):
    eff_sum = 0.0

    for x in range(0, 10):
        for y in range(0, 7):
            base_point_a = base_points_collect[x][y + 1]
            base_point_b = base_points_collect[x + 1][y]
            base_points_c = base_points_collect[x][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, duty_point)
            eff_sum += eff

        for y in range(0, 7):
            base_point_a = base_points_collect[x][y + 1]
            base_point_b = base_points_collect[x + 1][y + 1]
            base_points_c = base_points_collect[x + 1][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, duty_point)
            eff_sum += eff

    if eff_sum == 0.0:
        eff_sum = 0.74
    elif eff_sum > 1:
        eff_sum /= 2
    duty_point.update_data_relt_to_efficiency(eff_sum, rated_point)


def initiate_rated_point(request, project):
    turbo_list = initial_turbo_list()
    rp_inlet_temp = float(request.POST.get("rpInletTemp", 0))
    rp_inlet_humi = float(request.POST.get("rpInletHumidity", 0))
    rp_outlet_press = float(request.POST.get("rpOutletPressure", 0))
    point = RatedPoint(rp_inlet_temp, rp_inlet_humi, rp_outlet_press, 1, project, turbo_list)
    return point


def get_design_points_of_cond_one(request, point):
    duty_points_one = []
    cond_one_temp = float(request.POST.get("dp1InletTemp", 0))
    cond_one_humi = float(request.POST.get("dp1InletHumidity", 0))

    cond_one_point_one_flow = float(request.POST.get("dp1p1flow", 0)) / 100
    cond_one_point_one_press = float(request.POST.get("dp1p1Pressure", 0))

    cond_one_point_two_flow = float(request.POST.get("dp1p2flow", 0)) / 100
    cond_one_point_two_press = float(request.POST.get("dp1p2Pressure", 0))

    cond_one_point_three_flow = float(request.POST.get("dp1p3flow", 0)) / 100
    cond_one_point_three_press = float(request.POST.get("dp1p3Pressure", 0))

    cond_one_point_four_flow = float(request.POST.get("dp1p4flow", 0)) / 100
    cond_one_point_four_press = float(request.POST.get("dp1p4Pressure", 0))

    cond_one_point_five_flow = float(request.POST.get("dp1p5flow", 0)) / 100
    cond_one_point_five_press = float(request.POST.get("dp1p5Pressure", 0))

    cond_one_point_six_flow = float(request.POST.get("dp1p6flow", 0)) / 100
    cond_one_point_six_press = float(request.POST.get("dp1p6Pressure", 0))

    cond_one_relative_flow = [
        [cond_one_point_one_flow, cond_one_point_one_press],
        [cond_one_point_two_flow, cond_one_point_two_press],
        [cond_one_point_three_flow, cond_one_point_three_press],
        [cond_one_point_four_flow, cond_one_point_four_press],
        [cond_one_point_five_flow, cond_one_point_five_press],
        [cond_one_point_six_flow, cond_one_point_six_press]
    ]
    for y in cond_one_relative_flow:
        new_point = DutyPoint(cond_one_temp, cond_one_humi, y[1], y[0], point)
        duty_points_one.append(new_point)

    return duty_points_one


def get_design_points_of_cond_two(request, point):
    duty_points_two = []

    cond_two_temp = float(request.POST.get("dp2InletTemp", 0))
    cond_two_humi = float(request.POST.get("dp2InletHumidity", 0))

    cond_two_point_one_flow = float(request.POST.get("dp2p1flow", 0)) / 100
    cond_two_point_one_press = float(request.POST.get("dp2p1Pressure", 0))

    cond_two_point_two_flow = float(request.POST.get("dp2p2flow", 0)) / 100
    cond_two_point_two_press = float(request.POST.get("dp2p2Pressure", 0))

    cond_two_point_three_flow = float(request.POST.get("dp2p3flow", 0)) / 100
    cond_two_point_three_press = float(request.POST.get("dp2p3Pressure", 0))

    cond_two_point_four_flow = float(request.POST.get("dp2p4flow", 0)) / 100
    cond_two_point_four_press = float(request.POST.get("dp2p4Pressure", 0))

    cond_two_point_five_flow = float(request.POST.get("dp2p5flow", 0)) / 100
    cond_two_point_five_press = float(request.POST.get("dp2p5Pressure", 0))

    cond_two_point_six_flow = float(request.POST.get("dp2p6flow", 0)) / 100
    cond_two_point_six_press = float(request.POST.get("dp2p6Pressure", 0))

    cond_two_relative_flow = [
        [cond_two_point_one_flow, cond_two_point_one_press],
        [cond_two_point_two_flow, cond_two_point_two_press],
        [cond_two_point_three_flow, cond_two_point_three_press],
        [cond_two_point_four_flow, cond_two_point_four_press],
        [cond_two_point_five_flow, cond_two_point_five_press],
        [cond_two_point_six_flow, cond_two_point_six_press]
    ]
    for y in cond_two_relative_flow:
        new_point = DutyPoint(cond_two_temp, cond_two_humi, y[1], y[0], point)
        duty_points_two.append(new_point)
        
    return duty_points_two


def get_design_points_of_cond_three(request, point):
    duty_points_three = []

    cond_three_temp = float(request.POST.get("dp3InletTemp", 0))
    cond_three_humi = float(request.POST.get("dp3InletHumidity", 0))

    cond_three_point_one_flow = float(request.POST.get("dp3p1flow", 0)) / 100
    cond_three_point_one_press = float(request.POST.get("dp3p1Pressure", 0))

    cond_three_point_two_flow = float(request.POST.get("dp3p2flow", 0)) / 100
    cond_three_point_two_press = float(request.POST.get("dp3p2Pressure", 0))

    cond_three_point_three_flow = float(request.POST.get("dp3p3flow", 0)) / 100
    cond_three_point_three_press = float(request.POST.get("dp3p3Pressure", 0))

    cond_three_point_four_flow = float(request.POST.get("dp3p4flow", 0)) / 100
    cond_three_point_four_press = float(request.POST.get("dp3p4Pressure", 0))

    cond_three_point_five_flow = float(request.POST.get("dp3p5flow", 0)) / 100
    cond_three_point_five_press = float(request.POST.get("dp3p5Pressure", 0))

    cond_three_point_six_flow = float(request.POST.get("dp3p6flow", 0)) / 100
    cond_three_point_six_press = float(request.POST.get("dp3p6Pressure", 0))

    cond_three_relative_flow = [
        [cond_three_point_one_flow, cond_three_point_one_press],
        [cond_three_point_two_flow, cond_three_point_two_press],
        [cond_three_point_three_flow, cond_three_point_three_press],
        [cond_three_point_four_flow, cond_three_point_four_press],
        [cond_three_point_five_flow, cond_three_point_five_press],
        [cond_three_point_six_flow, cond_three_point_six_press]
    ]
    for y in cond_three_relative_flow:
        new_point = DutyPoint(cond_three_temp, cond_three_humi, y[1], y[0], point)
        duty_points_three.append(new_point)

    return duty_points_three


def interpolation_calculation(times, point, duty_points_collection, base_points_collection):
    for t in range(0, times):
        rated_point_interpolation(point, duty_points_collection, base_points_collection)
        for d in duty_points_collection:
            for d_p in d:
                duty_point_interpolation(d_p, point, base_points_collection)


def get_condition_graph_data(duty_points, base_points_collection, point):
    duty_point_one = duty_points[0]
    for x in base_points_collection:
        for y in x:
            y.update_data(point, duty_point_one)

    # 获取流量压力曲线数据
    cond_one_graph_points = []
    for x in base_points_collection:
        base_cond = []
        for y in x:
            single_point = [y.v, y.p]
            base_cond.append(single_point)
        cond_one_graph_points.append(base_cond)

    # 流量及轴功率曲线数据
    cond_one_power_points = []
    for x in duty_points:
        single_point = [x.actual_blower_inlet_flow_cubic, x.shaft_power]
        cond_one_power_points.append(single_point)

    # 设计工况点数据
    cond_one_design_points = []
    for x in duty_points:
        single_point = [x.actual_blower_inlet_flow_cubic, x.press_diff * 1000]
        cond_one_design_points.append(single_point)

    return [cond_one_graph_points, cond_one_power_points, cond_one_design_points]

def get_max_shaft_power(rated_point, duty_points_collection):
    max_shaft_power = rated_point.shaft_power
    for duty_points in duty_points_collection:
        for point in duty_points:
            if point.shaft_power > max_shaft_power:
                max_shaft_power = point.shaft_power
    return max_shaft_power


def get_motor_round_rating(max_shaft_power, rated_point):
    return round(max_shaft_power*(1+rated_point.motor_factor)/rated_point.de_rating, 0)


def initiate_motor_table():
    return [0, 55, 75, 90, 110, 132, 160, 200, 250, 315, 355, 400, 450,
            500, 560, 630, 710, 800, 900, 1000, 1120, 1250, 1400, 1560,
            1800, 2000, 2200, 2500]

def initiate_motor_power():
    return [0, 0.55, 0.75, 1.1, 1.5, 2.2,
            3.0, 3.7, 4.7, 5.5, 7.5, 9.2,
            11.0, 15.0]

def get_motor_size_from_motor_power(value, motor_power):
    length = len(motor_power)
    for index in range(0, length):
        if motor_power[index] > value:
            return motor_power[index]

    return motor_power[-1]

def get_motor_rating_from_motor(motor_round_rating, motor_table):
    length = len(motor_table)
    for index in range(0, length):
        if motor_table[index] > motor_round_rating:
            return motor_table[index]

    return motor_table[-1]



def get_motor_rating_from_torque(max_shaft_power, motor_factor):
    return max_shaft_power * (1 + motor_factor)


def get_motor_rating(rated_point, duty_points_collection, motor_table):
    max_shaft_power = get_max_shaft_power(rated_point, duty_points_collection)
    motor_round_rating = get_motor_round_rating(max_shaft_power, rated_point)
    if rated_point.project.volt < 700:
        return get_motor_rating_from_motor(motor_round_rating, motor_table)
    else:
        return get_motor_rating_from_torque(max_shaft_power, rated_point.motor_factor)

def least_square(x_array, y_array):
    t1, t2, t3, t4 = 0, 0, 0, 0
    for index in range(0, len(x_array)):
        t1 += x_array[index] ** 2
        t2 += x_array[index]
        t3 += x_array[index] * y_array[index]
        t4 += y_array[index]

    a = (t3 * len(x_array) - t2 * t4) / (t1 * len(x_array) - t2 * t2)
    b = (t1 * t4 - t2 * t3) / (t1 * len(x_array) - t2 * t2)
    return lambda x: a*x +b


def get_motor_loss_trend(motor_rating):
    load = [0.25, 0.5, 0.75, 1.0]
    shaft_power = [x * motor_rating for x in load]
    efficiency = [0.94, 0.962, 0.963, 0.963]
    loss_x = [x ** ORDEN for x in load]
    loss_y = []
    for index in range(0, len(loss_x)):
        loss_y.append(shaft_power[index] * (1 / efficiency[index] - 1))
    return least_square(loss_x, loss_y)


def calc_motor_data(duty_points_collection, motor_loss_trend, motor_rating):
    for duty_points in duty_points_collection:
        for point in duty_points:
            point.calc_motor_data(motor_loss_trend, motor_rating)

def initiate_glt_data():
    return {
        "GL1": {"oil_pump_capacity": 78},
        "GL2": {"oil_pump_capacity": 78},
        "GL3": {"oil_pump_capacity": 78},
        "GL5": {"oil_pump_capacity": 78},
        "GL8": {"oil_pump_capacity": 90},
        "GL10": {"oil_pump_capacity": 91},
        "GL15": {"oil_pump_capacity": 98},
        "GL20": {"oil_pump_capacity": 180},
        "GL30": {"oil_pump_capacity": 180},
        "GL50": {"oil_pump_capacity": 250},
    }

def get_oil_pump(rated_point, glt_data):
    selected_turbo = rated_point.selected_turbo.type
    oil_pump = glt_data[selected_turbo]["oil_pump_capacity"]
    return oil_pump


def get_oil_cooler_fan(gear_loss, motor_power):
    motor_size = get_motor_size_from_motor_power(0.0745*gear_loss, motor_power)
    return round(motor_size, 2)


def get_enclosure_cooling_fan_iteration(sum_loss, motor_power, amb_temp):
    x0 = 0
    for x in range(100):
        x1 = x0
        vcool = (sum_loss + x1)*1000/TEMP_RISE_AE/(3.5*290)*3600/(84200/(290*(273+amb_temp)))
        dp = 1.2*1.2*0.5*UAIR_MAX**2
        fan_pow = round(dp*(vcool)/3600/0.55/1000,1)
        x0 = get_motor_size_from_motor_power(fan_pow, motor_power)
        c = abs(x1 - x0)
        if c < 0.001:
            break
    return x0

def calc_heat_loss(rated_point, glt_data, max_mechanical_loss, amb_temp, motor_power, max_t2, max_motor_loss):

    oil_pump = get_oil_pump(rated_point, glt_data)
    pump_pow = oil_pump / 60000 * DO_OIL * 100 / 0.5

    control_panel = CONTROL_PANEL

    skin_heat_loss = calc_skin_heat_loss(amb_temp, oil_pump)

    gear_loss = max_mechanical_loss * 1.1 - skin_heat_loss
    oil_cooler_fan = get_oil_cooler_fan(gear_loss, motor_power)

    motor_loss_inside = max_motor_loss
    mechanical_loss_from_gearbox = 0.0
    main_lube_oil_pump = 0.0

    d2 = rated_point.selected_turbo.d2
    scroll_casing_surface = round(1.2 * (d2 / 350) ** 2, 2)
    heat_loss_scroll_casing = round(14*scroll_casing_surface*(max_t2 - amb_temp)/1000, 1)
    sum_loss_except_cooling_fan = motor_loss_inside + heat_loss_scroll_casing + skin_heat_loss \
                                    + mechanical_loss_from_gearbox + main_lube_oil_pump

    encolsure_cooling_fan = get_enclosure_cooling_fan_iteration(sum_loss_except_cooling_fan, motor_power, amb_temp)

    return pump_pow + control_panel + oil_cooler_fan + encolsure_cooling_fan


def calc_max_mechanical_loss(duty_points_collection):
    max_loss = 0
    for duty_points in duty_points_collection:
        for point in duty_points:
            if point.mechanical_losses > max_loss:
                max_loss = point.mechanical_losses

    return max_loss


def calc_max_t2(duty_points_collection):
    max_t2 = 0
    for duty_points in duty_points_collection:
        for point in duty_points:
            if point.t2 > max_t2:
                max_t2 = point.t2

    return max_t2

def cal_max_motor_loss(duty_points_collection):
    max_motor_loss = 0
    for duty_points in duty_points_collection:
        for point in duty_points:
            if point.motor_loss > max_motor_loss:
                max_motor_loss = point.motor_loss

    return max_motor_loss


def calc_skin_heat_loss(amb_temp, oil_pump):
    oil_system_surface = round((oil_pump**(1/3))**2*0.0223, 1)
    return round(14*oil_system_surface*(PLATE_SURFACE_TEMP-amb_temp)/1000, 1)


def update_total_wire_power(duty_points_collection, heat_loss):
    for duty_points in duty_points_collection:
        for point in duty_points:
            point.update_total_wire_power(heat_loss)


def get_table_data(rated_point, duty_points_collection):
    table_info = {
        "turbo": rated_point.selected_turbo.type,
        "condition1": {
            "temp": duty_points_collection[0][0].inlet_temp,
            "humidity": duty_points_collection[0][0].rh,
            "baraPressure": duty_points_collection[0][0].bara_pressure,
            "dataSet": []
        },
        "condition2": {
            "temp": duty_points_collection[1][0].inlet_temp,
            "humidity": duty_points_collection[1][0].rh,
            "baraPressure": duty_points_collection[1][0].bara_pressure,
            "dataSet": []
        },
        "condition3": {
            "temp": duty_points_collection[2][0].inlet_temp,
            "humidity": duty_points_collection[2][0].rh,
            "baraPressure": duty_points_collection[2][0].bara_pressure,
            "dataSet": []
        },

    }

    for index in range(0,3):
        for point in duty_points_collection[index]:
            data = {
                "relativeFlow": round(point.blower_capacity * 100, 1),
                "flowAmb": round(point.actual_flow_amb, 1),
                "outletPress": round(point.outlet_press, 3),
                "shaftPower": round(point.shaft_power, 1),
                "wirePower": round(point.total_wire_power, 1)
            }
            if index == 0:
                table_info["condition1"]["dataSet"].append(data)
            elif index == 1:
                table_info["condition2"]["dataSet"].append(data)
            elif index == 2:
                table_info["condition3"]["dataSet"].append(data)

    return table_info

def initiate_project(request):
    pj_name = request.POST.get("projectName", "")
    pj_serial_num = request.POST.get("projectNumber", "")
    pj_location = request.POST.get("projectLocation", "")
    pj_altitude = float(request.POST.get("projectAltitude", ""))
    pj_inlet_press = float(request.POST.get("projectInletPressure", ""))
    pj_frequency = int(request.POST.get("projectFrequency", ""))
    pj_machine_num = int(request.POST.get("projectMachNums", ""))
    pj_volt = int(request.POST.get("machVolt", ""))
    pj_security_coeff = float(request.POST.get("securityCoeff", ""))
    pj_ei_rating = int(request.POST.get("eiRating", ""))
    pj_amb_temp = float(request.POST.get("ambTemp", ""))
    pj_standard_flow = float(request.POST.get("ratedFlow", 0))
    pj_standard_press = float(request.POST.get("ratedPressure", 0))
    pj_standard_temp = float(request.POST.get("ratedTemp", 0))
    pj_standard_humi = float(request.POST.get("ratedHumidity", 0))
    return Project(pj_name, pj_serial_num, pj_location, MAX_FLOW_COEFF, PRESSURE_COEFF,
                   pj_altitude, pj_inlet_press, pj_frequency, pj_machine_num, pj_volt,
                   "ALU", pj_security_coeff, pj_ei_rating, pj_amb_temp, pj_standard_flow,
                   pj_standard_press, pj_standard_temp, pj_standard_humi)


class SelectView(LoginRequiredMixin, View):
    login_url = "/login"

    def get(self, request):
        return render(request, 'turbo_selection.html', {
            "turboActive": True
        })

    def post(self, request):

        selection_form = SelectionForm(request.POST)
        if selection_form.is_valid():
            pj = initiate_project(request)
            motor_table = initiate_motor_table()
            motor_power = initiate_motor_power()

            # 初始化额定工况点
            point = initiate_rated_point(request, pj)

            # 初始化三个工况下的各个设计工况点
            duty_points_one = get_design_points_of_cond_one(request, point)
            duty_points_two = get_design_points_of_cond_two(request, point)
            duty_points_three = get_design_points_of_cond_three(request, point)
            duty_points_collection = [duty_points_one, duty_points_two, duty_points_three]

            # 获取测试数据点
            base_points_collection = get_all_base_points()

            # 进行插值计算
            interpolation_calculation(10, point, duty_points_collection, base_points_collection)

            # 开始计算流量压力以及轴功率曲线
            cond_one_graph_data = get_condition_graph_data(duty_points_one, base_points_collection, point)
            cond_two_graph_data = get_condition_graph_data(duty_points_two, base_points_collection, point)
            cond_three_graph_data = get_condition_graph_data(duty_points_three, base_points_collection, point)

            # 计算进线功率
            # 首先获取motor_rating
            motor_rating = get_motor_rating(point, duty_points_collection, motor_table)
            motor_loss_trend = get_motor_loss_trend(motor_rating)
            calc_motor_data(duty_points_collection, motor_loss_trend, motor_rating)
            glt_data = initiate_glt_data()
            max_mechanical_loss = calc_max_mechanical_loss(duty_points_collection)
            max_t2 = calc_max_t2(duty_points_collection)
            max_motor_loss = cal_max_motor_loss(duty_points_collection)
            heat_loss = calc_heat_loss(point, glt_data, max_mechanical_loss, pj.amb_temp, motor_power, max_t2,
                                       max_motor_loss)
            update_total_wire_power(duty_points_collection, heat_loss)
            project_info = {"projectName": pj.name, "projectNumber": pj.serial_num}
            table_data = get_table_data(point, duty_points_collection)

            # 绘图所需数据
            graph_data = {
                "tableData": table_data,
                "projectInfo": project_info,
                "condOne": cond_one_graph_data,
                "condTwo": cond_two_graph_data,
                "condThree": cond_three_graph_data,
            }

            # 转换为json数据
            json_data = json.dumps(graph_data)

            # 初始化测试点
            return HttpResponse(
                json_data,
                content_type="application/json"
            )
        else:
            return HttpResponse(
                '{"status":"fail", "msg":"收藏出错"}',
                content_type='application/json')

