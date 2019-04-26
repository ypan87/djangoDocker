# !/usr/bin/python
# -*- coding: utf-8 -*-

import math
from .const import *
from selectedturbo.models import TestPoints

class BasePoint(object):

    def __init__(self, test_point=None):
        """
        Initialize the tested points. Data are collected through some field tests
        Arguments are listed as below:

        flow_coef          Flow coefficient of the tested point
        pressure_coef      Pressure coefficient of the tested point
        efficiency         Efficiency of the tested point
        flow_factor        Flow sky factor of the tested point
        pressure_factor    Pressure sky factor of the tested point
        efficiency_factor  Efficiency sky factor of the tested point
        """
        x = isinstance(test_point, TestPoints)
        self.flow_coef = test_point.flow_coef * test_point.flow_factor if x else 0
        self.pressure_coef = test_point.pressure_coef * test_point.pressure_factor if x else 0
        self.efficiency = test_point.efficiency * test_point.efficiency_factor if x else 0
        self.flow_factor = test_point.flow_factor if x else 0
        self.pressure_factor = test_point.pressure_factor if x else 0
        self.efficiency_factor = test_point.efficiency_factor if x else 0
        self.vinl = self.h_diff = self.p_diff = self.v = self.p = 0.0

    def update_data(self, rated_point, duty_point):
        d2 = rated_point.selected_turbo.d2/1000
        u2 = rated_point.u2
        rho_inlet = duty_point.air_cond.air_rho_inlet
        rho_amb = duty_point.air_cond.air_rho_amb
        k_k_minus_one = duty_point.k_k_minus_one
        rg = duty_point.air_cond.air_rg
        p0 = duty_point.p0
        pinl = p0 - duty_point.inlet_press_loss
        t0 = duty_point.amb_temp + KEL
        mass_flow = 1.0
        psi = 1.0
        bhp = 1.0
        self.vinl = self.flow_coef*math.pi*d2**2*u2*rho_inlet/rho_amb*3600/4*rated_point.cut_back_width
        self.h_diff = u2**2 * self.pressure_coef / 2
        self.p_diff = ((self.h_diff/(t0*k_k_minus_one*rg*self.efficiency)+1)**(1/(1/k_k_minus_one/self.efficiency))
                       *(p0-rho_amb*self.vinl**2*rated_point.c_inl_loss)-p0)*1000
        self.v = self.vinl * mass_flow
        self.p = self.p_diff * psi