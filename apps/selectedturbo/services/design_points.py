# !/usr/bin/python
# -*- coding: utf-8 -*-

import math

from .turbo_data import *
from .air import *
from .const import ORDEN

class DesignPoints(object):

    def __init__(self, inlet_temp, rh, outlet_press, flow_relative, bara_pressure=0.9880):
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
        self.efficiency = 0.8
        self.blower_capacity = flow_relative
        self.inlet_temp = inlet_temp
        self.rh = rh
        self.bara_pressure = bara_pressure
        self.outlet_press = outlet_press
        self.p0 = round(self.bara_pressure, 4)
        self.press_diff = round(self.outlet_press, 4)
        self.p2 = self.press_diff + self.p0
        self.amb_temp = round(self.inlet_temp, 2)
        self.gas_const = self.k_k_minus_one = 0.0
        self.poly_eff = self.poly_increase = 0.0
        self.psi = self.u2 = self.phi = 0.0
        self.actual_flow_amb = self.actual_blower_inlet_flow_cubic = 0.0
        self.actual_blower_inlet_flow_icfm = self.water_content = 0.0
        self.air_mass = self.compressor_relt_eff = 0.0
        self.impeller_power = self.mechanical_losses = 0.0
        self.shaft_power = self.motor_loss = self.terminal_power = self.total_wire_power = 0.0
        self.inlet_press_loss = self.dis_cone_press_loss = self.dpr = 0.0
        self.press_ratio = self.relt_phi = self.relt_psi = self.rho = 0.0
        self.t2 = self.rho2 = self.v2 = 0.0


class RatedPoint(DesignPoints):
    __mach = 0.0
    __mach_a = -0.0556168367569921
    __mach_b = 1.04437748333022
    # 额定工况点初始化
    def __init__(self,inlet_temp, rela_hum, outlet_press, flow_relative, project_info, turbo_list, bara_pressure=0.9880,
                 inlet_pres_loss=0.006, outlet_pres_loss=0.000):
        super(RatedPoint, self).__init__(inlet_temp, rela_hum, outlet_press, flow_relative, bara_pressure)
        self.turbo_list = turbo_list
        self.inlet_press_loss = round(inlet_pres_loss, 4)
        self.outlet_press_loss = outlet_pres_loss
        self.dis_cone_press_loss = round(self.outlet_press_loss, 4)
        self.dpr = (self.dis_cone_press_loss + self.p2) / (self.p0 - self.inlet_press_loss)
        self.mach = self.cut_back_width = 0.0
        self.mach_correction = 0.0
        self.selected_turbo = TurboData()
        self.gear_loss_fix = self.gear_loss_var = 0.0
        self.project = project_info
        self.press_ratio = self.p2 / (self.p0 - self.inlet_press_loss)
        self.relt_psi = 1.0
        self.n = 0.0
        self.c_inl_loss = 0.0
        self.air_cond = RatedPointAir(self.amb_temp, self.rh, self.inlet_press_loss, self.p0)
        self.rho = self.air_cond.air_rho_inlet
        self.__calc_pol()
        self.polytropic_eff_and_mach_iteration(0.5, 0)
        self.de_rating = 1 if self.project.amb_temp <= 45 else (155-self.project.amb_temp)/110
        self.motor_factor = 0.05


    # 计算额定工况点的相关数据
    def __calc_pol(self):
        self.gas_const = self.air_cond.air_rg
        self.k_k_minus_one = self.air_cond.air_k / (self.air_cond.air_k - 1)
        self.psi = self.project.pressure_coef
        self.actual_flow_amb = self.project.air_cond.air_flow * self.air_cond.air_amb_density
        self.actual_blower_inlet_flow_cubic = self.project.air_cond.air_flow * self.air_cond.air_inlet_density
        self.actual_blower_inlet_flow_icfm = self.actual_blower_inlet_flow_cubic / ACFM
        self.water_content = self.air_cond.air_x * 100
        self.air_mass = self.actual_blower_inlet_flow_cubic * self.air_cond.air_rho_inlet / 3600
        self.c_inl_loss = self.inlet_press_loss / self.air_cond.air_rho_amb / self.actual_flow_amb**2

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
            poly_increase = abs(self.amb_temp+273.15)*self.k_k_minus_one*self.gas_const*x1*(((self.p2+self.dis_cone_press_loss)
                            /(self.p0-self.inlet_press_loss))**(1/self.k_k_minus_one/x1)-1)
            u2 = (poly_increase * 2 / self.project.pressure_coef)**0.5
            tur = self.select_turbo(self.turbo_list, self.project, u2)
            size_correction = tur.size_correction
            if y1 <= 0.8:
                correction = 1 * size_correction
            else:
                correction = (y1 * self.__mach_a + self.__mach_b) * size_correction
            x0 = self.efficiency * correction
            y0 = u2 / self.air_cond.air_csound
            c = abs(x1-x0) + abs(y1-y0)
            self.selected_turbo = tur
            if c < 0.0001:
                break
        self.__update_pol_data(x0, y0, correction)


    # 更新工况中与polytropic efficiency 和 mach number相关的数据
    def __update_pol_data(self, poly_eff_val, mach_number_val, correction):
        self.mach_correction = correction
        self.poly_eff = poly_eff_val
        self.mach = mach_number_val
        self.poly_increase = (self.amb_temp+KEL)*self.k_k_minus_one*self.gas_const*self.poly_eff*(((self.p2+self.dis_cone_press_loss)
                            /(self.p0-self.inlet_press_loss))**(1/self.k_k_minus_one/self.poly_eff)-1)
        self.u2 = (self.poly_increase * 2 / self.psi)**0.5
        turbo_d2 = self.selected_turbo.d2
        self.cut_back_width = self.selected_turbo.cut_back
        self.phi = self.actual_blower_inlet_flow_cubic * 4 / 3600 / (math.pi * (turbo_d2/ 1000) ** 2 *self.u2) / self.cut_back_width
        self.compressor_relt_eff = 1
        self.impeller_power = self.poly_increase / self.poly_eff / 1000 * self.air_mass
        self.gear_loss_fix = self.selected_turbo.fix_loss_1 * self.poly_increase + self.selected_turbo.fix_loss_2
        self.gear_loss_var = self.selected_turbo.var_loss
        self.mechanical_losses = self.gear_loss_fix + self.gear_loss_var * self.impeller_power
        self.shaft_power = self.mechanical_losses + self.impeller_power
        self.relt_phi = self.phi / self.project.max_flow_coef
        self.n = self.u2 / (math.pi * turbo_d2 / 1000) * 60
        self.t2 = self.poly_increase / self.poly_eff / self.k_k_minus_one / self.gas_const + self.amb_temp
        self.rho2 = self.p2 * 100000 / ((self.t2 + KEL) * self.gas_const)
        self.v2 = self.air_mass / self.rho2 * 3600


    # 更新鼓风机选择列表，并返回选定的鼓风机数据
    def select_turbo(self, t_list, relt_project, u2):
        selected_turbo = self.selected_turbo
        time = 0
        for x in t_list:
            x.coeff = self.actual_blower_inlet_flow_cubic*0.00111111111111111 \
                      /(math.pi*(x.d2/1000)**2*u2)/x.cut_back
            if x.coeff <= relt_project.max_flow_coef:
                x.val = 1
                time += 1
                if time == 1:
                    selected_turbo = x
            else:
                x.val = 0

        return selected_turbo


class DutyPoint(DesignPoints):

    def __init__(self,inlet_temp, rela_hum, outlet_press, flow_relative, rated_point, bara_pressure=0.9880):
        super(DutyPoint, self).__init__(inlet_temp, rela_hum, outlet_press, flow_relative, bara_pressure)
        self.efficiency = 0.8
        self.air_cond = DutyPointAir(self.amb_temp, self.rh, self.p0)
        self.inlet_press_loss_iteration(rated_point)
        self.__calc_pol()
        self.update_data_relt_to_rated_point(rated_point)

    # 计算额定工况点的相关数据
    def __calc_pol(self):
        self.gas_const = self.air_cond.air_rg
        self.k_k_minus_one = self.air_cond.air_k / (self.air_cond.air_k - 1)
        self.water_content = self.air_cond.air_x * 100

    # 计算并更新与ratedPoint相关的数据
    def update_data_relt_to_rated_point(self, rated_point):
        self.u2 = rated_point.u2
        self.actual_flow_amb = rated_point.project.air_cond.air_flow * self.air_cond.air_amb_density * self.blower_capacity
        self.poly_eff = self.efficiency * rated_point.mach_correction
        self.compressor_relt_eff = self.poly_eff / rated_point.poly_eff
        self.relative_data_iteration_and_update(rated_point)


    def relative_data_iteration_and_update(self, rated_point):
        self.inlet_press_loss_iteration(rated_point)
        self.dis_cone_press_loss_iteration(rated_point)

    # 已知额定点，求工况点的inlet_press_loss
    def inlet_press_loss_iteration(self, rated_point):
        x0 = self.inlet_press_loss
        for x in range(100):
            x1 = x0
            blower_flow = rated_point.project.air_cond.air_flow * self.blower_capacity \
                          * (self.air_cond.air_t0+273.15)/273.15*(1+self.air_cond.air_x_logic)*1.01325 \
                          / (self.air_cond.air_p0-x1)*self.air_cond.air_rg/RAIR
            rho_inlet = (self.p0-x1)*100000/(self.air_cond.air_rg*(self.air_cond.air_t0+KEL))
            x0 = rated_point.inlet_press_loss*(blower_flow/rated_point.actual_blower_inlet_flow_cubic)**2*rho_inlet/rated_point.air_cond.air_rho_inlet
            c = abs(x1 - x0)
            if c < 0.001:
                break
        self.__update_data_relt_to_inlet_press_loss(x0, rated_point)

    def dis_cone_press_loss_iteration(self, rated_point):
        x0 = self.dis_cone_press_loss
        for x in range(100):
            x1 = x0
            poly_increase = (self.amb_temp + KEL) * self.k_k_minus_one * self.gas_const * self.poly_eff * (((self.p2 + x1) / (self.p0 - self.inlet_press_loss) )**(1/self.k_k_minus_one/self.poly_eff) - 1)
            t2 = poly_increase / self.poly_eff / self.k_k_minus_one / self.gas_const + self.amb_temp
            rho2 = self.p2 * 100000 / ((t2 + KEL) * self.gas_const)
            v2 = self.air_mass / rho2 * 3600
            x0 = rated_point.dis_cone_press_loss * (v2 / rated_point.v2) **2 * rho2 / rated_point.rho2
            c = abs(x1 - x0)
            if c < 0.001:
                break
        self.__update_data_relt_to_dis_cone_press_loss(x0, rated_point)


    def __update_data_relt_to_inlet_press_loss(self, inlet_press_loss, rated_point):
        self.inlet_press_loss = round(inlet_press_loss,4)
        self.actual_blower_inlet_flow_cubic = rated_point.project.air_cond.air_flow * self.blower_capacity \
                                              * (self.air_cond.air_t0+273.15)/273.15*(1+self.air_cond.air_x_logic)*1.01325 \
                                              / (self.air_cond.air_p0-self.inlet_press_loss)*self.air_cond.air_rg/RAIR
        self.actual_blower_inlet_flow_icfm = self.actual_blower_inlet_flow_cubic / ACFM
        self.air_cond.air_rho_inlet = (self.p0-self.inlet_press_loss)*100000/(self.air_cond.air_rg*(self.air_cond.air_t0+KEL))
        self.air_cond.air_inlet_density = (self.air_cond.air_t0+273.15)/273.15*(1+self.air_cond.air_x_logic)*1.01325 \
                                          /(self.air_cond.air_p0-self.inlet_press_loss)*self.air_cond.air_rg/RAIR
        self.air_mass = self.actual_blower_inlet_flow_cubic * self.air_cond.air_rho_inlet / 3600
        self.press_ratio = self.p2 / (self.p0 - self.inlet_press_loss)
        self.rho = self.air_cond.air_rho_inlet

    def __update_data_relt_to_dis_cone_press_loss(self, dis_cone_press_loss, rated_point):
        self.dis_cone_press_loss = dis_cone_press_loss
        self.poly_increase = (self.amb_temp + KEL) * self.k_k_minus_one * self.gas_const * self.poly_eff * \
                             (((self.p2 + dis_cone_press_loss) / (self.p0 - self.inlet_press_loss)) ** (1 / self.k_k_minus_one / self.poly_eff) - 1)
        self.t2 = self.poly_increase / self.poly_eff / self.k_k_minus_one / self.gas_const + self.amb_temp
        self.rho2 = self.p2 * 100000 / ((self.t2 + KEL) * self.gas_const)
        self.v2 = self.air_mass / self.rho2 * 3600
        self.dpr = (self.p2 + dis_cone_press_loss) / (self.p0 - self.inlet_press_loss)
        self.psi = self.poly_increase * 2 / self.u2 ** 2
        self.phi = self.actual_blower_inlet_flow_cubic * 4 / 3600 / (math.pi * (rated_point.selected_turbo.d2/1000)**2*self.u2)/rated_point.cut_back_width
        self.impeller_power = self.poly_increase / self.poly_eff / 1000 * self.air_mass
        self.mechanical_losses = rated_point.gear_loss_fix + self.impeller_power * rated_point.gear_loss_var
        self.shaft_power = self.impeller_power + self.mechanical_losses
        self.relt_phi = self.phi / rated_point.project.max_flow_coef
        self.relt_psi = self.psi / rated_point.project.pressure_coef

    def update_data_relt_to_efficiency(self, efficiency, rated_point):
        self.efficiency = efficiency
        self.poly_eff = self.efficiency * rated_point.mach_correction
        self.compressor_relt_eff = self.poly_eff / rated_point.poly_eff
        self.dis_cone_press_loss_iteration(rated_point)

    def update_rated_point(self, rated_point):
        rated_point.p0 = 1111


    def calc_motor_data(self, motor_trend_func, motor_rating):
        load_calc = self.shaft_power / motor_rating
        loss_x = load_calc ** ORDEN
        loss_y = motor_trend_func(loss_x)
        self.motor_loss = loss_y
        self.terminal_power = self.shaft_power + self.motor_loss

    def update_total_wire_power(self, heat_loss):
        self.total_wire_power = self.terminal_power + heat_loss

