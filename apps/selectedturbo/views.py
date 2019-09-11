import math
import json
import xlsxwriter
import io

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from .services.project import Project
from .services.design_points import RatedPoint, DutyPoint
from .services.base_points import BasePoint
from .services.turbo_data import TurboData
from .services.const import *
from .models import Turbo, TestPoints
from .services.efficiency_points import *
from .services.turbo_calculation import *
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SelectionForm
from utils.form_validation import form_validation_errors

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


def get_all_base_points(turbo_calculation, category="GL3"):
    base_points_collection = []
    for x in range(1, 12):
        condition_collection = []
        for y in range (1, 9):
            point_set = TestPoints.objects.filter(working_condition=x, working_position=y)[:1]
            for point in point_set:
                base_point = BasePoint(point)
                condition_collection.append(base_point)
        base_points_collection.append(condition_collection)
    turbo_calculation.add_base_point_list(base_points_collection)

def single_triangle_calculation(base_point_a, base_point_b, base_point_c, design_point_d):
    ab = ((base_point_a.final_flow_coef - base_point_b.final_flow_coef)**2
          + (base_point_a.final_pressure_coef - base_point_b.final_pressure_coef)**2)**0.5
    bc = ((base_point_b.final_flow_coef - base_point_c.final_flow_coef)**2
          + (base_point_b.final_pressure_coef - base_point_c.final_pressure_coef)**2)**0.5
    ac = ((base_point_a.final_flow_coef - base_point_c.final_flow_coef)**2
          + (base_point_a.final_pressure_coef - base_point_c.final_pressure_coef)**2)**0.5

    angle_bac = angle_b(ab, bc, ac)
    area_abc = area(ab, ac, angle_bac)

    da = ((base_point_a.final_flow_coef - design_point_d.phi)**2 + (base_point_a.final_pressure_coef - design_point_d.psi)**2)**0.5
    db = ((base_point_b.final_flow_coef - design_point_d.phi)**2 + (base_point_b.final_pressure_coef - design_point_d.psi)**2)**0.5
    dc = ((base_point_c.final_flow_coef - design_point_d.phi)**2 + (base_point_c.final_pressure_coef - design_point_d.psi)**2)**0.5

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
        eff_interpolation = (base_point_a.final_efficiency * area_dbc + base_point_b.final_efficiency * area_dac
                            + base_point_c.final_efficiency * area_abd) / area_abc

    return eff_interpolation, area_ratio


def angle_b(a, b, c):
    return math.acos((a**2 + c**2 - b**2) / (2 * a * c) )


def area(a, c, angle):
    return 0.5 * math.sin(angle) * a * c

def initiate_rated_point(post_data, project, turbo_calculation):
    rp_inlet_temp = float(post_data.get("ratingPointInletTmep", 0))
    rp_inlet_humi = float(post_data.get("ratingPointHumi", 0))
    rp_outlet_press = float(post_data.get("ratingPointOutPressure", 0))
    rp_inlet_press = float(post_data.get("ratingPointInletPressure", 0))
    rp_inlet_press_loss = float(post_data.get("ratingPointInletLoss", 0))
    rp_outlet_press_loss = float(post_data.get("ratingPointOutletLoss", 0))
    is_imperial = get_is_imperial(post_data)
    point = RatedPoint(rp_inlet_temp, rp_inlet_humi, rp_outlet_press, 1,
                       project, is_imperial, False, rp_inlet_press, rp_inlet_press_loss,
                       rp_outlet_press_loss)
    turbo_calculation.add_rated_point(point)

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
    return round(max_shaft_power*(1+rated_point.motor_factor)/rated_point.project.de_rating, 0)


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
    selected_turbo = rated_point.project.selected_turbo.type
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

    d2 = rated_point.project.selected_turbo.d2
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
        "turbo": rated_point.project.selected_turbo.type,
        "cutBack": rated_point.project.selected_turbo.cut_back,
        "conditions": [],
    }

    for duty_points in duty_points_collection:
        info_array = {
            "temp": duty_points[0].inlet_temp,
            "humidity": duty_points[0].rh,
            "baraPressure": duty_points[0].bara_pressure,
            "dataSet": []
        }
        table_info["conditions"].append(info_array)
        for point in duty_points:
            data = {
                "relativeFlow": round(point.blower_capacity * 100, 1),
                "flowAmb": round(point.actual_flow_amb, 1),
                "outletPress": round(point.outlet_press, 3),
                "shaftPower": round(point.shaft_power, 1),
                "wirePower": round(point.total_wire_power, 1)
            }
            info_array["dataSet"].append(data)

    return table_info

def get_is_imperial(post_data):
    if post_data.get("isImperial") == "metric":
        return False
    else:
        return True

# 初始化project TODO 项目初始化有需要更新
def initiate_project(post_data):
    turbo_list = initial_turbo_list()
    pj_name = post_data.get("projectName", "")
    pj_serial_num = post_data.get("projectNumber", "")
    pj_location = post_data.get("projectLocation", "")
    pj_altitude = float(post_data.get("projectAltitude", ""))
    pj_inlet_press = float(post_data.get("projectInletPres", ""))
    # pj_frequency = int(post_data.get("projectFrequency", ""))
    pj_machine_num = int(post_data.get("projectUnitsNum", ""))
    pj_volt = int(post_data.get("projectVolt", ""))
    pj_security_coeff = float(post_data.get("projectSafetyFactor", ""))
    pj_ei_rating = int(post_data.get("projectEIRating", ""))
    pj_amb_temp = float(post_data.get("projectEnvTemp", ""))
    pj_standard_flow = float(post_data.get("ratingFlow", 0))
    pj_standard_press = float(post_data.get("ratingPressure", 0))
    pj_standard_temp = float(post_data.get("ratingTemp", 0))
    pj_standard_humi = float(post_data.get("ratingHumi", 0))
    # pj_is_wet = float(post_data.get("is_wet", False))
    pj_is_imperial = get_is_imperial(post_data)
    pj_max_flow_coeff = float(post_data.get("maxFlowCoeff", 0))
    pj_pressure_coeff = float(post_data.get("maxPressureCoeff", 0))

    return Project(pj_name, pj_serial_num, pj_location, pj_max_flow_coeff,
                   pj_pressure_coeff, turbo_list, pj_altitude, pj_is_imperial, False,
                   pj_inlet_press, 50, pj_machine_num, pj_volt, "ALU", pj_security_coeff,
                   pj_ei_rating, pj_amb_temp, pj_standard_flow, pj_standard_press,
                   pj_standard_temp, pj_standard_humi)

# 初始化效率曲线
def initial_efficiency_points_list():
     efficiency_points_list = [
         [
             [0.85, 0.09, 1.23],
             [0.85, 0.0975, 1.18],
             [0.85, 0.1050, 1.05],
             [0.85, 0.1, 1.05],
             [0.85, 0.095, 1.04],
             [0.85, 0.09, 1.035],
             [0.85, 0.08, 1.04],
             [0.85, 0.07, 1.05],
             [0.85, 0.065, 1.075],
             [0.85, 0.057, 1.12],
             [0.85, 0.055, 1.2],
             [0.85, 0.06, 1.23],
             [0.85, 0.07, 1.26],
             [0.85, 0.075, 1.27],
             [0.85, 0.08, 1.265],
         ],
         [
             [0.8, 0.1125, 1.08],
             [0.8, 0.1125, 0.95],
             [0.8, 0.088, 0.92],
             [0.8, 0.077, 0.91],
             [0.8, 0.067, 0.92],
             [0.8, 0.054, 0.96],
             [0.8, 0.045, 1.01],
             [0.8, 0.042, 1.05],
             [0.8, 0.041, 1.14],
             [0.8, 0.043, 1.18],
         ],
         [
             [0.75, 0.1175, 0.98],
             [0.75, 0.113, 0.86],
             [0.75, 0.1, 0.84],
             [0.75, 0.083, 0.8],
             [0.75, 0.058, 0.825],
             [0.75, 0.04, 0.95],
             [0.75, 0.035, 1.0],
             [0.75, 0.036, 1.12],
         ]
     ]
     efficiency_curve = []
     for efficiency_points in efficiency_points_list:
         condition_list = []
         for point in efficiency_points:
            efficiency_point = EfficiencyPoint(point[0], point[1], point[2])
            condition_list.append(efficiency_point)
         efficiency_curve.append(condition_list)

     return efficiency_curve

def print_obj(object):
    for x,y in object.__dict__.items():
        print("%s:%s" % (x, y))

# 获取工况曲线所有工况点的集合
def get_single_condition_collection(condition, post_data):
    inlet_pressure = float(condition[0].get("pressure"))
    temp = float(condition[1].get('temp'))
    humi = float(condition[2].get('humi'))
    is_imperial = get_is_imperial(post_data)

    single_length = len(condition)
    duty_point_collection = []
    for x in range(3, single_length):
        flow = float(condition[x].get("flow")) / 100
        pressure = float(condition[x].get("pressure"))
        duty_point = DutyPoint(temp, humi, pressure, flow, False, is_imperial, inlet_pressure)
        duty_point_collection.append(duty_point)
    return duty_point_collection

# 获取普通工况点集合
def get_normal_points(post_data, turbo_calculation):
    condition_array = post_data.get('conditionArray', [])
    condition_collection = []
    for condition in condition_array:
        duty_points_collection = get_single_condition_collection(condition, post_data)
        condition_collection.append(duty_points_collection)
    turbo_calculation.add_duty_point_list(condition_collection)

# 插值计算
def interpolation_calculation(times, point, normal_points_collection, base_points_collection):
    for t in range(0, times):
        rated_point_interpolation(point, normal_points_collection, base_points_collection)
        for d in normal_points_collection:
            for d_p in d:
                normal_point_interpolation(d_p, point, base_points_collection)

# 额定工况点插值计算
def rated_point_interpolation(rated_point, normal_points_collection, base_points_collection):

    eff_sum = calculate_efficiency_sum(base_points_collection, rated_point)

    rated_point.update_data_relt_to_efficiency(eff_sum)
    for x in normal_points_collection:
        for y in x:
            y.update_data_relt_to_rated_point(rated_point)

# 普通工况点插值计算
def normal_point_interpolation(normal_point, rated_point, base_points_collection):

    eff_sum = calculate_efficiency_sum(base_points_collection, normal_point)

    normal_point.update_data_relt_to_efficiency(eff_sum, rated_point)

# 使用插值法算出某个工况点的效率插值总值
def calculate_efficiency_sum(base_points_collection, design_point):
    eff_sum = 0
    a_len = len(base_points_collection) - 1
    b_len = len(base_points_collection[0]) - 1
    for x in range(0, a_len):
        for y in range(0, b_len):
            base_point_a = base_points_collection[x][y+1]
            base_point_b = base_points_collection[x+1][y]
            base_points_c = base_points_collection[x][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, design_point)
            eff_sum += eff

        for y in range(0, b_len):
            base_point_a = base_points_collection[x][y+1]
            base_point_b = base_points_collection[x+1][y+1]
            base_points_c = base_points_collection[x+1][y]
            eff, _ = single_triangle_calculation(base_point_a, base_point_b, base_points_c, design_point)
            eff_sum += eff

    if eff_sum == 0.0:
        eff_sum = 0.74
    elif eff_sum > 1:
        eff_sum /= 2

    return eff_sum

# 获取测试点数据
def get_base_points_table_data(base_points_collection):
    base_table = []
    for points in base_points_collection:
        points_array = []
        for point in points:
            single_pair = [point.final_flow_coef, point.final_pressure_coef]
            points_array.append(single_pair)
        base_table.append(points_array)
    return base_table

# 获取效率点数据
def get_efficient_table_data(efficiency_points_collection):
    efficiency_table = []
    for points in efficiency_points_collection:
        points_array = []
        for point in points:
            single_pair = [point.flow_coeff, point.pressure_coeff]
            points_array.append(single_pair)
        efficiency_table.append(points_array)
    return efficiency_table

# 获取普通工况点数据
def get_normal_points_table_data(normal_points_collection):
    normal_points_table = []
    for points in normal_points_collection:
        points_array = []
        for point in points:
            single_pair = [point.phi, point.psi]
            points_array.append(single_pair)
        normal_points_table.append(points_array)
    return normal_points_table

# 获取额定工况点数据
def get_rated_point_table_data(rated_point):
    return [rated_point.phi, rated_point.psi]

# 获取返回数据
def get_turbo_efficiency_graph(rated_point, normal_points_collection,
                               efficiency_points_collection, base_points_collection):
    base_points_table = get_base_points_table_data(base_points_collection)
    efficiency_points_table = get_efficient_table_data(efficiency_points_collection)
    normal_points_table = get_normal_points_table_data(normal_points_collection)
    rated_point_table = get_rated_point_table_data(rated_point)
    return {
        "baseTableData": base_points_table,
        "efficiencyTableData": efficiency_points_table,
        "normalTableData": normal_points_table,
        "ratedTableData": rated_point_table
    }

class SelectView(View):
    login_url = "/login"

    def get(self, request):
        return render(request, 'turbo.html')

    def post(self, request):

        # TODO 数据验证
        post_data = json.loads(request.body.decode())
        # TODO round 精度差距
        turbo_calculation = TurboCalculation()
        pj = initiate_project(post_data)

        # 初始化额定工况点
        initiate_rated_point(post_data, pj, turbo_calculation)
        # 计算鼓风机的选择
        turbo_calculation.calculate_selected_turbo()

        # 获取测试点
        get_all_base_points(turbo_calculation)

        # 获取普通工况点
        get_normal_points(post_data, turbo_calculation)

        # 进行插值计算
        turbo_calculation.interpolation_calculation(10)

        # 获取最终返回数据
        final_table_data = turbo_calculation.get_all_data()

        return HttpResponse(
            json.dumps(final_table_data),
            content_type="application/json",
        )

class ExcelView(View):
    def post(self, request):
        data = [
            ["风机型号：GL1","40C/90%"],
            ["进气压力", "0.988 bara"],
            ["相对流量", "ΔP", "流量", "轴功率"],
            ["%", "barG", "m3/h", "kW"],
            [45, 0.6, 1812.6, 47.3],
            [60, 0.6, 2416.9, 47.3],
            [70, 0.6, 2819.7, 53.8],
            [80, 0.6, 3222.5, 60.4],
            [90, 0.6, 3625.3, 67.6],
            [100, 0.6, 4028.1, 78.6],
        ]
        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        for row_num, columns in enumerate(data):
            for col_num, cell_data in enumerate(columns):
                worksheet.write(row_num, col_num, cell_data)

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

        worksheet.merge_range('B1:D1', data[0][1], merge_format)
        worksheet.merge_range('B2:D2', data[1][1], merge_format)

        chart = workbook.add_chart({'type': 'line'})

        chart.add_series({
            'name': '',
            'categories': '=Sheet1!$C$10:$C$5',
            'values': '=Sheet1!$D$10:$D$5',
        })

        worksheet.insert_chart('A12', chart, {'x_offset': 25, 'y_offset': 10})

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = 'turbo_result.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response