# !/usr/bin/python
# -*- coding: utf-8 -*-

import math
from .efficiency_points import EfficiencyPoint
from .const import *

class TurboCalculation(object):

    def __init__(self):
        self.base_point_list = []
        self.rated_point = None
        self.duty_point_list = []
        self.efficiency_point_list = self.initial_efficiency_points_list()
        self.motor_table = self.initiate_motor_table()
        self.motor_power = self.initiate_motor_power()
        self.glt_data = self.initiate_glt_data()

    # 初始化效率曲线
    def initial_efficiency_points_list(self):
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

    def initiate_motor_table(self):
        return [0, 55, 75, 90, 110, 132, 160, 200, 250, 315, 355, 400, 450,
                500, 560, 630, 710, 800, 900, 1000, 1120, 1250, 1400, 1560,
                1800, 2000, 2200, 2500]

    def initiate_motor_power(self):
        return [0, 0.55, 0.75, 1.1, 1.5, 2.2,
                3.0, 3.7, 4.7, 5.5, 7.5, 9.2,
                11.0, 15.0]

    def initiate_glt_data(self):
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

    def add_base_point_list(self, base_point_list):
        self.base_point_list = base_point_list

    def add_rated_point(self, rated_point):
        self.rated_point = rated_point

    def add_duty_point_list(self, duty_point_list):
        self.duty_point_list = duty_point_list
        for duty_points in duty_point_list:
            for duty_point in duty_points:
                duty_point.initialize_partial_variables(self.rated_point)

    def calculate_selected_turbo(self):
        self.rated_point.calculate_selected_turbo()

    def interpolation_calculation(self, times):
        for time in range(0, times):
            self.rated_point_interpolation()
            for point_list in self.duty_point_list:
                for point in point_list:
                    self.normal_point_interpolation(point)

    def rated_point_interpolation(self):
        eff_sum = self.calculate_efficiency_sum(self.rated_point)
        self.rated_point.update_data_relt_to_efficiency(eff_sum)
        for duty_points in self.duty_point_list:
            for duty_point in duty_points:
                duty_point.update_data_relt_to_rated_point(self.rated_point)

    # 普通工况点插值计算
    def normal_point_interpolation(self, duty_point):
        eff_sum = self.calculate_efficiency_sum(duty_point)
        duty_point.update_data_relt_to_efficiency(eff_sum, self.rated_point)

    # 使用插值法算出某个工况点的效率插值总值
    def calculate_efficiency_sum(self, design_point):
        eff_sum = 0
        a_len = len(self.base_point_list) - 1
        b_len = len(self.base_point_list[0]) - 1
        for x in range(0, a_len):
            for y in range(0, b_len):
                base_point_a = self.base_point_list[x][y + 1]
                base_point_b = self.base_point_list[x + 1][y]
                base_points_c = self.base_point_list[x][y]
                eff, _ = self.single_triangle_calculation(base_point_a, base_point_b, base_points_c, design_point)
                eff_sum += eff

            for y in range(0, b_len):
                base_point_a = self.base_point_list[x][y + 1]
                base_point_b = self.base_point_list[x + 1][y + 1]
                base_points_c = self.base_point_list[x + 1][y]
                eff, _ = self.single_triangle_calculation(base_point_a, base_point_b, base_points_c, design_point)
                eff_sum += eff

        if eff_sum == 0.0:
            eff_sum = 0.74
        elif eff_sum > 1:
            eff_sum /= 2

        return eff_sum

    def single_triangle_calculation(self, base_point_a, base_point_b, base_point_c, design_point):
        ab = ((base_point_a.final_flow_coef - base_point_b.final_flow_coef) ** 2
              + (base_point_a.final_pressure_coef - base_point_b.final_pressure_coef) ** 2) ** 0.5
        bc = ((base_point_b.final_flow_coef - base_point_c.final_flow_coef) ** 2
              + (base_point_b.final_pressure_coef - base_point_c.final_pressure_coef) ** 2) ** 0.5
        ac = ((base_point_a.final_flow_coef - base_point_c.final_flow_coef) ** 2
              + (base_point_a.final_pressure_coef - base_point_c.final_pressure_coef) ** 2) ** 0.5

        angle_bac = self.angle_b(ab, bc, ac)
        area_abc = self.area(ab, ac, angle_bac)

        da = ((base_point_a.final_flow_coef - design_point.phi) ** 2 + (
        base_point_a.final_pressure_coef - design_point.psi) ** 2) ** 0.5
        db = ((base_point_b.final_flow_coef - design_point.phi) ** 2 + (
        base_point_b.final_pressure_coef - design_point.psi) ** 2) ** 0.5
        dc = ((base_point_c.final_flow_coef - design_point.phi) ** 2 + (
        base_point_c.final_pressure_coef - design_point.psi) ** 2) ** 0.5

        angle_bad = self.angle_b(ab, db, da)
        angle_dac = self.angle_b(ac, dc, da)
        angle_bdc = self.angle_b(db, bc, dc)

        area_abd = self.area(ab, da, angle_bad)
        area_dac = self.area(ac, da, angle_dac)
        area_dbc = self.area(db, dc, angle_bdc)

        area_sum = area_abd + area_dac + area_dbc

        area_ratio = area_abc / area_sum

        eff_interpolation = 0.0

        if area_ratio > 0.999:
            eff_interpolation = (base_point_a.final_efficiency * area_dbc + base_point_b.final_efficiency * area_dac
                                 + base_point_c.final_efficiency * area_abd) / area_abc

        return eff_interpolation, area_ratio

    def angle_b(self, a, b, c):
        return math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))

    def area(self, a, c, angle):
        return 0.5 * math.sin(angle) * a * c

    def get_efficiency_graph_data(self):
        base_points_table = self.get_base_points_table_data()
        efficiency_points_table = self.get_efficient_table_data()
        normal_points_table = self.get_normal_points_table_data()
        rated_point_table = self.get_rated_point_table_data()
        return {
            "baseTableData": base_points_table,
            "efficiencyTableData": efficiency_points_table,
            "normalTableData": normal_points_table,
            "ratedTableData": rated_point_table
        }

    # 获取测试点数据
    def get_base_points_table_data(self):
        base_table = []
        for points in self.base_point_list:
            points_array = []
            for point in points:
                single_pair = [point.final_flow_coef, point.final_pressure_coef]
                points_array.append(single_pair)
            base_table.append(points_array)
        return base_table

    # 获取效率点数据
    def get_efficient_table_data(self):
        efficiency_table = []
        for points in self.efficiency_point_list:
            points_array = []
            for point in points:
                single_pair = [point.flow_coeff, point.pressure_coeff]
                points_array.append(single_pair)
            efficiency_table.append(points_array)
        return efficiency_table

    # 获取普通工况点数据
    def get_normal_points_table_data(self):
        normal_points_table = []
        for points in self.duty_point_list:
            points_array = []
            for point in points:
                single_pair = [point.phi, point.psi]
                points_array.append(single_pair)
            normal_points_table.append(points_array)
        return normal_points_table

    # 获取额定工况点数据
    def get_rated_point_table_data(self):
        return [self.rated_point.phi, self.rated_point.psi]

    def get_conditions_graph_data(self):
        conditions = []
        for points in self.duty_point_list:
            graph_data = self.get_single_condition_graph_data(points)
            conditions.append(graph_data)
        return conditions

    def get_single_condition_graph_data(self, duty_points):
        duty_point_one = duty_points[0]
        for x in self.base_point_list:
            for y in x:
                y.update_data(self.rated_point, duty_point_one)

        # 获取流量压力曲线数据
        cond_one_graph_points = []
        for x in self.base_point_list:
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

    def get_table_data(self):
        motor_rating = self.get_motor_rating()
        motor_loss_trend = self.get_motor_loss_trend(motor_rating)
        self.calc_motor_data(motor_loss_trend, motor_rating)
        max_mechanical_loss = self.calc_max_mechanical_loss()
        max_t2 = self.calc_max_t2()
        max_motor_loss = self.cal_max_motor_loss()
        heat_loss = self.calc_heat_loss(max_mechanical_loss, max_t2, max_motor_loss)
        self.update_total_wire_power(heat_loss)
        table_data = self.get_cond_table_data()
        return table_data

    def get_motor_rating(self):
        max_shaft_power = self.get_max_shaft_power()
        motor_round_rating = self.get_motor_round_rating(max_shaft_power)
        if self.rated_point.project.volt < 700:
            return self.get_motor_rating_from_motor(motor_round_rating)
        else:
            return self.get_motor_rating_from_torque(max_shaft_power)

    def get_max_shaft_power(self):
        max_shaft_power = self.rated_point.shaft_power
        for duty_points in self.duty_point_list:
            for point in duty_points:
                if point.shaft_power > max_shaft_power:
                    max_shaft_power = point.shaft_power
        return max_shaft_power

    def get_motor_round_rating(self, max_shaft_power):
        return round(max_shaft_power * (1 + self.rated_point.motor_factor) / self.rated_point.project.de_rating, 0)

    def get_motor_rating_from_motor(self, motor_round_rating):
        length = len(self.motor_table)
        for index in range(0, length):
            if self.motor_table[index] > motor_round_rating:
                return self.motor_table[index]

        return self.motor_table[-1]

    def get_motor_rating_from_torque(self, max_shaft_power):
        return max_shaft_power * (1 + self.rated_point.motor_factor)

    def get_motor_loss_trend(self, motor_rating):
        load = [0.25, 0.5, 0.75, 1.0]
        shaft_power = [x * motor_rating for x in load]
        efficiency = [0.94, 0.962, 0.963, 0.963]
        loss_x = [x ** ORDEN for x in load]
        loss_y = []
        for index in range(0, len(loss_x)):
            loss_y.append(shaft_power[index] * (1 / efficiency[index] - 1))
        return self.least_square(loss_x, loss_y)

    def least_square(self, x_array, y_array):
        t1, t2, t3, t4 = 0, 0, 0, 0
        for index in range(0, len(x_array)):
            t1 += x_array[index] ** 2
            t2 += x_array[index]
            t3 += x_array[index] * y_array[index]
            t4 += y_array[index]

        a = (t3 * len(x_array) - t2 * t4) / (t1 * len(x_array) - t2 * t2)
        b = (t1 * t4 - t2 * t3) / (t1 * len(x_array) - t2 * t2)
        return lambda x: a * x + b

    def calc_motor_data(self, motor_loss_trend, motor_rating):
        for duty_points in self.duty_point_list:
            for point in duty_points:
                point.calc_motor_data(motor_loss_trend, motor_rating)

    def calc_max_mechanical_loss(self):
        max_loss = 0
        for duty_points in self.duty_point_list:
            for point in duty_points:
                if point.mechanical_losses > max_loss:
                    max_loss = point.mechanical_losses

        return max_loss

    def calc_max_t2(self):
        max_t2 = 0
        for duty_points in self.duty_point_list:
            for point in duty_points:
                if point.t2 > max_t2:
                    max_t2 = point.t2

        return max_t2

    def cal_max_motor_loss(self):
        max_motor_loss = 0
        for duty_points in self.duty_point_list:
            for point in duty_points:
                if point.motor_loss > max_motor_loss:
                    max_motor_loss = point.motor_loss

        return max_motor_loss

    def calc_heat_loss(self, max_mechanical_loss, max_t2, max_motor_loss):
        amb_temp = self.rated_point.project.amb_temp
        oil_pump = self.get_oil_pump()
        pump_pow = oil_pump / 60000 * DO_OIL * 100 / 0.5

        control_panel = CONTROL_PANEL

        skin_heat_loss = self.calc_skin_heat_loss(amb_temp, oil_pump)

        gear_loss = max_mechanical_loss * 1.1 - skin_heat_loss
        oil_cooler_fan = self.get_oil_cooler_fan(gear_loss)

        motor_loss_inside = max_motor_loss
        mechanical_loss_from_gearbox = 0.0
        main_lube_oil_pump = 0.0

        d2 = self.rated_point.project.selected_turbo.d2
        scroll_casing_surface = round(1.2 * (d2 / 350) ** 2, 2)
        heat_loss_scroll_casing = round(14 * scroll_casing_surface * (max_t2 - amb_temp) / 1000, 1)
        sum_loss_except_cooling_fan = motor_loss_inside + heat_loss_scroll_casing + skin_heat_loss \
                                      + mechanical_loss_from_gearbox + main_lube_oil_pump

        encolsure_cooling_fan = self.get_enclosure_cooling_fan_iteration(sum_loss_except_cooling_fan, amb_temp)

        return pump_pow + control_panel + oil_cooler_fan + encolsure_cooling_fan

    def get_oil_pump(self):
        selected_turbo = self.rated_point.project.selected_turbo.type
        oil_pump = self.glt_data[selected_turbo]["oil_pump_capacity"]
        return oil_pump

    def calc_skin_heat_loss(self, amb_temp, oil_pump):
        oil_system_surface = round((oil_pump ** (1 / 3)) ** 2 * 0.0223, 1)
        return round(14 * oil_system_surface * (PLATE_SURFACE_TEMP - amb_temp) / 1000, 1)

    def get_oil_cooler_fan(self, gear_loss):
        motor_size = self.get_motor_size_from_motor_power(0.0745 * gear_loss)
        return round(motor_size, 2)

    def get_motor_size_from_motor_power(self, value):
        length = len(self.motor_power)
        for index in range(0, length):
            if self.motor_power[index] > value:
                return self.motor_power[index]

        return self.motor_power[-1]

    def get_enclosure_cooling_fan_iteration(self, sum_loss, amb_temp):
        x0 = 0
        for x in range(100):
            x1 = x0
            vcool = (sum_loss + x1) * 1000 / TEMP_RISE_AE / (3.5 * 290) * 3600 / (84200 / (290 * (273 + amb_temp)))
            dp = 1.2 * 1.2 * 0.5 * UAIR_MAX ** 2
            fan_pow = round(dp * (vcool) / 3600 / 0.55 / 1000, 1)
            x0 = self.get_motor_size_from_motor_power(fan_pow)
            c = abs(x1 - x0)
            if c < 0.001:
                break
        return x0

    def update_total_wire_power(self, heat_loss):
        for duty_points in self.duty_point_list:
            for point in duty_points:
                point.update_total_wire_power(heat_loss)

    def get_cond_table_data(self):
        table_info = {
            "turbo": self.rated_point.project.selected_turbo.type,
            "cutBack": self.rated_point.project.selected_turbo.cut_back,
            "conditions": [],
        }

        for duty_points in self.duty_point_list:
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

    def get_project_data(self):
        return {
            "projectName": self.rated_point.project.name,
            "projectNumber": self.rated_point.project.serial_num
        }

    def get_all_data(self):
        eff_graph_data = self.get_efficiency_graph_data()
        conditions_graph_data = self.get_conditions_graph_data()
        project_data = self.get_project_data()
        table_data = self.get_table_data()
        return dict(eff_graph_data,
                    **{
                        "conditions": conditions_graph_data,
                        "tableData": table_data,
                        "projectInfo": project_data
                    })
