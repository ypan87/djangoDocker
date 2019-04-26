import math
import json

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from .services.project import Project
from .services.design_points import RatedPoint, DutyPoint
from .services.base_points import BasePoint
from .services.turbo_data import TurboData
from .models import Turbo, TestPoints
from django.contrib.auth.mixins import LoginRequiredMixin


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

    cond_one_point_one_flow = float(request.POST.get("dp1p1flow", 0))
    cond_one_point_one_press = float(request.POST.get("dp1p1Pressure", 0))

    cond_one_point_two_flow = float(request.POST.get("dp1p2flow", 0))
    cond_one_point_two_press = float(request.POST.get("dp1p2Pressure", 0))

    cond_one_point_three_flow = float(request.POST.get("dp1p3flow", 0))
    cond_one_point_three_press = float(request.POST.get("dp1p3Pressure", 0))

    cond_one_point_four_flow = float(request.POST.get("dp1p4flow", 0))
    cond_one_point_four_press = float(request.POST.get("dp1p4Pressure", 0))

    cond_one_point_five_flow = float(request.POST.get("dp1p5flow", 0))
    cond_one_point_five_press = float(request.POST.get("dp1p5Pressure", 0))

    cond_one_point_six_flow = float(request.POST.get("dp1p6flow", 0))
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

    cond_two_point_one_flow = float(request.POST.get("dp2p1flow", 0))
    cond_two_point_one_press = float(request.POST.get("dp2p1Pressure", 0))

    cond_two_point_two_flow = float(request.POST.get("dp2p2flow", 0))
    cond_two_point_two_press = float(request.POST.get("dp2p2Pressure", 0))

    cond_two_point_three_flow = float(request.POST.get("dp2p3flow", 0))
    cond_two_point_three_press = float(request.POST.get("dp2p3Pressure", 0))

    cond_two_point_four_flow = float(request.POST.get("dp2p4flow", 0))
    cond_two_point_four_press = float(request.POST.get("dp2p4Pressure", 0))

    cond_two_point_five_flow = float(request.POST.get("dp2p5flow", 0))
    cond_two_point_five_press = float(request.POST.get("dp2p5Pressure", 0))

    cond_two_point_six_flow = float(request.POST.get("dp2p6flow", 0))
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

    cond_three_point_one_flow = float(request.POST.get("dp3p1flow", 0))
    cond_three_point_one_press = float(request.POST.get("dp3p1Pressure", 0))

    cond_three_point_two_flow = float(request.POST.get("dp3p2flow", 0))
    cond_three_point_two_press = float(request.POST.get("dp3p2Pressure", 0))

    cond_three_point_three_flow = float(request.POST.get("dp3p3flow", 0))
    cond_three_point_three_press = float(request.POST.get("dp3p3Pressure", 0))

    cond_three_point_four_flow = float(request.POST.get("dp3p4flow", 0))
    cond_three_point_four_press = float(request.POST.get("dp3p4Pressure", 0))

    cond_three_point_five_flow = float(request.POST.get("dp3p5flow", 0))
    cond_three_point_five_press = float(request.POST.get("dp3p5Pressure", 0))

    cond_three_point_six_flow = float(request.POST.get("dp3p6flow", 0))
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


class SelectView(LoginRequiredMixin, View):
    login_url = "/login"

    def get(self, request):
        return render(request, 'turbo_selection.html')

    def post(self, request):

        # TODO 获取表单，进行验证
        # selection_form = SelectionForm(request.POST)
        # if selection_form.is_valid():
            # 初始化项目信息
            # TODO 确定是否需要根据输入信息初始化
            # max_flow_coef = 0.1089
            # pressure_coef = 1.1250
            # pj = Project(max_flow_coef, pressure_coef)
        # else:
        #     return HttpResponse(
        #         '{"status":"fail", "msg":"收藏出错"}',
        #         content_type='application/json')

        max_flow_coef = 0.1089
        pressure_coef = 1.1250
        pj = Project(max_flow_coef, pressure_coef)
        
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

        # 绘图所需数据
        graph_data = {
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

