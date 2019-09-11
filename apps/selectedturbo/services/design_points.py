# !/usr/bin/python
# -*- coding: utf-8 -*-

import math

from .air import *
from utils.utility import *

# 设计工况点
class DesignPoints(object):

    def __init__(self, inlet_temp, rh, outlet_press, flow_relative, bara_pressure, is_imperial, is_wet):
        """
        Initialize the design points, including the rating points and 18 other points
        which belongs to 3 duties
        All the arguments are listed as below:

        inlet_temp         Inlet temperature of the turbo
        rela_hum           Relative humidity of the point
        flow               The designed flow of the point
        # pressure           The designed pressure of the point

        bara_pressure      Barometric pressure
        inlet_pres_loss    The inlet pressure loss
        outlet_press_loss  The outlet pressure loss
        """
        self.is_imperial = is_imperial
        self.is_wet = is_wet
        self.efficiency = 0.8
        self.blower_capacity = flow_relative
        self.inlet_temp = inlet_temp
        self.rh = rh
        self.bara_pressure = bara_pressure
        self.outlet_press = outlet_press
        self.p0 = self.press_diff = self.p2 = self.amb_temp = None
        self.gas_const = self.k_k_minus_one = None
        self.poly_eff = self.poly_increase = None
        self.psi = self.u2 = self.phi = None
        self.actual_flow_amb = self.actual_blower_inlet_flow_cubic = None
        self.actual_blower_inlet_flow_icfm = self.water_content = None
        self.air_mass = self.compressor_relt_eff = None
        self.impeller_power = self.mechanical_losses = None
        self.shaft_power = self.motor_loss = self.terminal_power = self.total_wire_power = None
        self.inlet_press_loss = self.dis_cone_press_loss = self.dpr = None
        self.press_ratio = self.relt_phi = self.relt_psi = self.rho = None
        self.t2 = self.rho2 = self.v2 = self.air_cond = None

# 额定工况点
class RatedPoint(DesignPoints):
    __mach = 0.0
    __mach_a = -0.0556168367569921
    __mach_b = 1.04437748333022
    # 额定工况点初始化
    def __init__(self,inlet_temp, rela_hum, outlet_press, flow_relative, project, is_imperial=False,
                 is_wet=False, bara_pressure=0.9880, inlet_press_loss=0.006, outlet_press_loss=0.000):
        super(RatedPoint, self).__init__(inlet_temp, rela_hum, outlet_press,
                                        flow_relative, bara_pressure, is_imperial, is_wet)
        self.project = project
        self.outlet_press_loss = outlet_press_loss
        self.inlet_press_loss_original = inlet_press_loss
        self.mach = self.mach_correction = None
        self.gear_loss_fix = self.gear_loss_var = None
        self.n = self.c_inl_loss = self.rho = None
        self.motor_factor = 0.05
        self.relt_psi = 1.0
        self.initialize_partial_variables()

    def initialize_partial_variables(self):
        self.calculate_amb_temp()
        self.calculate_inlet_pressure_loss()
        self.calculate_press_diff()
        self.calculate_dis_cone_press_loss()
        self.calculate_p0()
        self.calculate_p2()
        self.calculate_dpr()
        self.calculate_press_ratio()
        self.air_cond = RatedPointAir(self.amb_temp, self.rh, self.inlet_press_loss, self.is_wet, self.p0)
        self.rho = self.air_cond.air_rho_inlet
        self.calculate_gas_const()
        self.calculate_k_k_minus_one()
        self.calculate_psi()
        self.calculate_actual_flow_amb()
        self.calculate_actual_blower_inlet_flow_cubic()
        self.calculate_actual_blower_inlet_flow_icfm()
        self.calculate_water_content()
        self.calculate_air_mass()
        self.calculate_c_inl_loss()

    def calculate_amb_temp(self):
        self.amb_temp = round(imperial_metric_value_to_metric(self.inlet_temp, self.is_imperial, TEMP),2)

    def calculate_inlet_pressure_loss(self):
        self.inlet_press_loss = round(imperial_metric_value_to_metric(self.inlet_press_loss_original, self.is_imperial, PRES), 4)

    def calculate_press_diff(self):
        self.press_diff = round(imperial_metric_value_to_metric(self.outlet_press, self.is_imperial, PRES),4)

    def calculate_dis_cone_press_loss(self):
        self.dis_cone_press_loss = round(imperial_metric_value_to_metric(self.outlet_press_loss, self.is_imperial, PRES), 4)

    def calculate_p0(self):
        self.p0 = round(imperial_metric_value_to_metric(self.bara_pressure, self.is_imperial, PRES), 4)

    def calculate_p2(self):
        self.p2 = self.p0 + self.press_diff

    def calculate_dpr(self):
        self.dpr = (self.dis_cone_press_loss + self.p2) / (self.p0 - self.inlet_press_loss)

    def calculate_press_ratio(self):
        self.press_ratio = self.p2 / (self.p0 - self.inlet_press_loss)

    def calculate_gas_const(self):
        self.gas_const = self.air_cond.air_rg

    def calculate_k_k_minus_one(self):
        self.k_k_minus_one = self.air_cond.air_k / (self.air_cond.air_k - 1)

    def calculate_psi(self):
        self.psi = self.project.pressure_coef

    def calculate_actual_flow_amb(self):
        self.actual_flow_amb = self.project.air_cond.air_flow * self.air_cond.air_amb_density

    def calculate_actual_blower_inlet_flow_cubic(self):
        self.actual_blower_inlet_flow_cubic = self.project.air_cond.air_flow * self.air_cond.air_inlet_density

    def calculate_actual_blower_inlet_flow_icfm(self):
        self.actual_blower_inlet_flow_icfm = self.actual_blower_inlet_flow_cubic / ACFM

    def calculate_water_content(self):
        self.water_content = self.air_cond.air_x * 100

    def calculate_air_mass(self):
        self.air_mass = self.actual_blower_inlet_flow_cubic * self.air_cond.air_rho_inlet / 3600

    def calculate_c_inl_loss(self):
        self.c_inl_loss = self.inlet_press_loss / self.air_cond.air_rho_amb / self.actual_flow_amb**2

    # 计算 Polytropic Enthalpy Increase
    def calculate_poly_increase(self, poly_eff):
        self.poly_increase = (self.amb_temp+KEL)*self.k_k_minus_one*self.gas_const*poly_eff*(((self.p2+self.dis_cone_press_loss)
                            /(self.p0-self.inlet_press_loss))**(1/self.k_k_minus_one/poly_eff)-1)

    # 计算u2
    def calculate_u2(self):
        self.u2 = (self.poly_increase * 2 / self.psi)**0.5

    # 计算phi
    def calculate_phi(self):
        self.phi = self.actual_blower_inlet_flow_cubic * 4 / 3600 / \
                   (math.pi * (self.project.selected_turbo.d2 / 1000) ** 2 *self.u2) / self.project.selected_turbo.cut_back

    # 计算impeller power
    def calculate_impeller_power(self):
        self.impeller_power = self.poly_increase / self.poly_eff / 1000 * self.air_mass

    # 计算gear loss fix
    def calculate_gear_loss_fix(self):
        self.gear_loss_fix = self.project.selected_turbo.fix_loss_1 * self.poly_increase + self.project.selected_turbo.fix_loss_2
        self.project.gear_loss_fix = self.gear_loss_fix

    # 计算gear loss var
    def calculate_gear_loss_var(self):
        self.gear_loss_var = self.project.selected_turbo.var_loss
        self.project.gear_loss_var = self.gear_loss_var

    # 计算mechanical_loss
    def calculate_mechanical_loss(self):
        self.mechanical_losses = self.gear_loss_fix + self.gear_loss_var * self.impeller_power

    # 计算shaft power
    def calculate_shaft_power(self):
        self.shaft_power = self.mechanical_losses + self.impeller_power

    # 计算relative phi
    def calculate_relative_phi(self):
        self.relt_phi = self.phi / self.project.max_flow_coef

    # 计算n
    def calculate_n(self):
        self.n = self.u2 / (math.pi * self.project.selected_turbo.d2 / 1000) * 60

    # 计算t2
    def calculate_t2(self):
        self.t2 = self.poly_increase / self.poly_eff / self.k_k_minus_one / self.gas_const + self.amb_temp

    # 计算rho2
    def calculate_rho2(self):
        self.rho2 = self.p2 * 100000 / ((self.t2 + KEL) * self.gas_const)

    # 计算v2
    def calculate_v2(self):
        self.v2 = self.air_mass / self.rho2 * 3600

    # 计算应该选择的鼓风机类型
    # TODO 有可能选择不到合适的鼓风机
    def calculate_selected_turbo(self):
        self.polytropic_eff_and_mach_iteration(0.5, 0)

    # 当更新efficiency时，更新其他的数据
    def update_data_relt_to_efficiency(self, efficiency):
        self.efficiency = efficiency
        self.polytropic_eff_and_mach_iteration(self.poly_eff, self.mach)

    # 使用迭代计算算出polytropic efficiency和mach number，并更新鼓风机数据和鼓风机选型
    def polytropic_eff_and_mach_iteration(self, poly_eff_initial, mach_initial):
        x0, y0 = poly_eff_initial, mach_initial
        correction = 0.0
        for x in range(100):
            x1, y1 = x0, y0
            self.calculate_poly_increase(x1)
            self.calculate_u2()
            tur = self.select_turbo(self.u2)
            size_correction = tur.size_correction
            if y1 <= 0.8:
                correction = 1 * size_correction
            else:
                correction = (y1 * self.__mach_a + self.__mach_b) * size_correction
            x0 = self.efficiency * correction
            y0 = self.u2 / self.air_cond.air_csound
            c = abs(x1-x0) + abs(y1-y0)
            self.project.selected_turbo = tur
            if c < 0.0001:
                break
        self.__update_pol_data(x0, y0, correction)

    # 更新工况中与polytropic efficiency 和 mach number相关的数据
    def __update_pol_data(self, poly_eff_val, mach_number_val, correction):
        self.mach_correction = correction
        self.poly_eff = poly_eff_val
        self.mach = mach_number_val
        self.calculate_phi()
        self.compressor_relt_eff = 1
        self.calculate_impeller_power()
        self.calculate_gear_loss_fix()
        self.calculate_gear_loss_var()
        self.calculate_mechanical_loss()
        self.calculate_shaft_power()
        self.calculate_relative_phi()
        self.calculate_n()
        self.calculate_t2()
        self.calculate_rho2()
        self.calculate_v2()

    # 更新鼓风机选择列表，并返回选定的鼓风机数据
    def select_turbo(self, u2):
        selected_turbo = self.project.selected_turbo
        time = 0
        for x in self.project.turbo_list:
            x.coeff = self.actual_blower_inlet_flow_cubic*0.00111111111111111 \
                      /(math.pi*(x.d2/1000)**2*u2)/x.cut_back
            if x.coeff <= self.project.max_flow_coef:
                x.val = 1
                time += 1
                if time == 1:
                    selected_turbo = x
            else:
                x.val = 0

        return selected_turbo

# 普通工况点
class DutyPoint(DesignPoints):

    def __init__(self, inlet_temp, rela_hum, outlet_press, flow_relative, is_wet=False, is_imperial=False, bara_pressure=0.9880):
        super(DutyPoint, self).__init__(inlet_temp, rela_hum, outlet_press, flow_relative,
                                        bara_pressure, is_imperial, is_wet)

    def initialize_partial_variables(self, rated_point):
        self.inlet_press_loss = self.dis_cone_press_loss = 0.0
        self.calculate_p0()
        self.calculate_press_diff()
        self.calculate_p2()
        self.calculate_amb_temp()
        self.air_cond = DutyPointAir(self.amb_temp, self.rh, self.is_wet, self.p0)
        self.inlet_press_loss_iteration(rated_point)
        self.calculate_gas_const()
        self.calculate_k_k_minus_one()
        self.calculate_water_content()
        self.calculate_u2(rated_point)
        self.calculate_actual_flow_amb(rated_point)
        self.calculate_poly_eff(rated_point)
        self.calculate_compressor_relt_eff(rated_point)
        self.dis_cone_press_loss_iteration(rated_point)

    # 已知额定点，求工况点的inlet_press_loss
    def inlet_press_loss_iteration(self, rated_point):
        x0 = self.inlet_press_loss
        for x in range(100):
            x1 = x0
            self.calculate_actual_blower_inlet_flow_cubic(rated_point)
            self.calculate_air_cond_rho_inlet(x1)
            try:
                x0 = self.calculate_inlet_press_loss_literal(rated_point)
            except:
                x0 = 0.006
            c = abs(x1 - x0)
            if c < 0.001:
                break
        self.__update_data_relt_to_inlet_press_loss(x0)

    # 计算与inlet_press_loss相关的属性
    def __update_data_relt_to_inlet_press_loss(self, inlet_press_loss):
        self.inlet_press_loss = round(inlet_press_loss,4)
        self.calculate_actual_blower_inlet_flow_icfm()
        self.calculate_air_cond_inlet_density()
        self.calculate_air_mass()
        self.calculate_press_ratio()
        self.calculate_rho()

    def dis_cone_press_loss_iteration(self, rated_point):
        x0 = self.dis_cone_press_loss
        for x in range(100):
            x1 = x0
            self.calculate_poly_increase(x1)
            self.calculate_t2()
            self.calculate_rho2()
            self.calculate_v2()
            x0 = self.calculate_dis_cone_press_loss_literal(rated_point)
            c = abs(x1 - x0)
            if c < 0.001:
                break
        self.__update_data_relt_to_dis_cone_press_loss(x0, rated_point)

    def __update_data_relt_to_dis_cone_press_loss(self, dis_cone_press_loss, rated_point):
        self.dis_cone_press_loss = dis_cone_press_loss
        self.calculate_dpr()
        self.calculate_psi()
        self.calculate_phi(rated_point)
        self.calculate_impeller_power()
        self.calculate_mechanical_loss(rated_point)
        self.calculate_shaft_power()
        self.calculate_relt_phi(rated_point)
        self.calculate_relt_psi(rated_point)

    # 计算并更新与ratedPoint相关的数据
    def update_data_relt_to_rated_point(self, rated_point):
        self.calculate_u2(rated_point)
        self.calculate_actual_flow_amb(rated_point)
        self.calculate_poly_eff(rated_point)
        self.calculate_compressor_relt_eff(rated_point)
        self.relative_data_iteration_and_update(rated_point)

    def relative_data_iteration_and_update(self, rated_point):
        self.inlet_press_loss_iteration(rated_point)
        self.dis_cone_press_loss_iteration(rated_point)

    def update_data_relt_to_efficiency(self, efficiency, rated_point):
        self.efficiency = efficiency
        self.calculate_poly_eff(rated_point)
        self.calculate_compressor_relt_eff(rated_point)
        self.dis_cone_press_loss_iteration(rated_point)

    def calculate_p0(self):
        self.p0 = round(imperial_metric_value_to_metric(self.bara_pressure, self.is_imperial, PRES), 4)

    def calculate_p2(self):
        self.p2 = self.p0 + self.press_diff

    def calculate_press_diff(self):
        self.press_diff = round(imperial_metric_value_to_metric(self.outlet_press, self.is_imperial, PRES),4)

    def calculate_amb_temp(self):
        self.amb_temp = round(imperial_metric_value_to_metric(self.inlet_temp, self.is_imperial, TEMP),2)

    def calculate_gas_const(self):
        self.gas_const = self.air_cond.air_rg

    def calculate_k_k_minus_one(self):
        self.k_k_minus_one = self.air_cond.air_k / (self.air_cond.air_k - 1)

    def calculate_water_content(self):
        self.water_content = self.air_cond.air_x * 100

    # 计算 actual blower inlet flow cubic
    def calculate_actual_blower_inlet_flow_cubic(self, rated_point):
        self.actual_blower_inlet_flow_cubic = rated_point.project.air_cond.air_flow * self.blower_capacity \
                                              * (self.air_cond.air_t0 + 273.15) / 273.15 * (
                                              1 + self.air_cond.air_x_logic) * 1.01325 \
                                              / (self.air_cond.air_p0 - self.inlet_press_loss) * self.air_cond.air_rg / RAIR

    def calculate_air_cond_rho_inlet(self, inlet_press_loss):
        self.air_cond.air_rho_inlet = (self.p0-inlet_press_loss)*100000/(self.air_cond.air_rg*(self.air_cond.air_t0+KEL))

    # 计算inlet press的公式（没有迭代计算）
    def calculate_inlet_press_loss_literal(self, rated_point):
        return rated_point.inlet_press_loss*(self.actual_blower_inlet_flow_cubic / rated_point.actual_blower_inlet_flow_cubic)**2*self.air_cond.air_rho_inlet \
               /rated_point.air_cond.air_rho_inlet

    # 计算 actual blower inlet flow icfm
    def calculate_actual_blower_inlet_flow_icfm(self):
        self.actual_blower_inlet_flow_icfm = self.actual_blower_inlet_flow_cubic / ACFM

    # 计算 air inlet density
    def calculate_air_cond_inlet_density(self):
        self.air_cond.air_inlet_density = (self.air_cond.air_t0+273.15)/273.15*(1+self.air_cond.air_x_logic)*1.01325 \
                                          /(self.air_cond.air_p0-self.inlet_press_loss)*self.air_cond.air_rg/RAIR

    # 计算 air mass
    def calculate_air_mass(self):
        self.air_mass = self.actual_blower_inlet_flow_cubic * self.air_cond.air_rho_inlet / 3600

    # 计算 pressure ratio
    def calculate_press_ratio(self):
        self.press_ratio = self.p2 / (self.p0 - self.inlet_press_loss)

    # 计算 rho
    def calculate_rho(self):
        self.rho = self.air_cond.air_rho_inlet

    # 计算 u2
    def calculate_u2(self, rated_point):
        self.u2 = rated_point.u2

    # 计算 actual flow amb
    def calculate_actual_flow_amb(self, rated_point):
        self.actual_flow_amb = rated_point.project.air_cond.air_flow * self.air_cond.air_amb_density * self.blower_capacity

    # 计算 poly eff
    def calculate_poly_eff(self, rated_point):
        self.poly_eff = self.efficiency * rated_point.mach_correction

    # 计算 compressor relative eff
    def calculate_compressor_relt_eff(self, rated_point):
        self.compressor_relt_eff = self.poly_eff / rated_point.poly_eff

    # 计算 poly increase
    def calculate_poly_increase(self, dis_cone_press_loss):
        self.poly_increase = (self.amb_temp + KEL) * self.k_k_minus_one * self.gas_const * self.poly_eff * \
                             (((self.p2 + dis_cone_press_loss) / (self.p0 - self.inlet_press_loss) )**(1/self.k_k_minus_one/self.poly_eff) - 1)

    # 计算 t2
    def calculate_t2(self):
        self.t2 = self.poly_increase / self.poly_eff / self.k_k_minus_one / self.gas_const + self.amb_temp

    # 计算 rho2
    def calculate_rho2(self):
        self.rho2 = self.p2 * 100000 / ((self.t2 + KEL) * self.gas_const)

    # 计算 v2
    def calculate_v2(self):
        self.v2 = self.air_mass / self.rho2 * 3600

    # 计算 discharge cone pressure loss
    def calculate_dis_cone_press_loss_literal(self, rated_point):
        return rated_point.dis_cone_press_loss * (self.v2 / rated_point.v2) **2 * self.rho2 / rated_point.rho2

    # 计算dpr
    def calculate_dpr(self):
        self.dpr = (self.p2 + self.dis_cone_press_loss) / (self.p0 - self.inlet_press_loss)

    # 计算psi
    def calculate_psi(self):
        self.psi = self.poly_increase * 2 / self.u2 ** 2

    # 计算phi
    def calculate_phi(self, rated_point):
        self.phi = self.actual_blower_inlet_flow_cubic * 4 / 3600 / \
                   (math.pi * (rated_point.project.selected_turbo.d2/1000)**2*self.u2)\
                   /rated_point.project.selected_turbo.cut_back

    # 计算 impeller power
    def calculate_impeller_power(self):
        self.impeller_power = self.poly_increase / self.poly_eff / 1000 * self.air_mass

    # 计算 mechanical loss
    def calculate_mechanical_loss(self, rated_point):
        self.mechanical_losses = rated_point.gear_loss_fix + self.impeller_power * rated_point.gear_loss_var

    # 计算 shaft power
    def calculate_shaft_power(self):
        self.shaft_power = self.impeller_power + self.mechanical_losses

    # 计算 relative phi
    def calculate_relt_phi(self, rated_point):
        self.relt_phi = self.phi / rated_point.project.max_flow_coef

    # 计算 relative psi
    def calculate_relt_psi(self, rated_point):
        self.relt_psi = self.psi / rated_point.project.pressure_coef

    def calc_motor_data(self, motor_trend_func, motor_rating):
        load_calc = self.shaft_power / motor_rating
        loss_x = load_calc ** ORDEN
        loss_y = motor_trend_func(loss_x)
        self.motor_loss = loss_y
        self.terminal_power = self.shaft_power + self.motor_loss

    def update_total_wire_power(self, heat_loss):
        self.total_wire_power = self.terminal_power + heat_loss

