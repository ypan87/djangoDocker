# !/usr/bin/python
# -*- coding: utf-8 -*-

from .const import *

class MoistureAir(object):
    """
    initialize the attributes under different condition
    """
    def __init__(self, air_t0, air_rh, air_p0 = 0.988):
        self.air_t0 = air_t0
        self.air_rh = air_rh
        self.air_p0 = air_p0
        self.air_pd = (0.00625108065+0.00043381882*self.air_t0 + 0.000017341077*self.air_t0**2
                       + 0.0000001210936*self.air_t0**3 + 0.000000006292408 * self.air_t0**4)*98066.5
        self.air_x = self.air_rh / 100 * self.air_pd * 0.62184 / (+self.air_p0 * 100000 - self.air_pd * self.air_rh / 100)
        self.air_cph20 = (1.8684+0.0095*(self.air_t0/100)+0.00373*(self.air_t0/100)**2)*1000
        self.air_cpair = RAIR * 3.5
        self.air_rg = (self.air_x*RH2O+RAIR)/(1+self.air_x)
        self.air_x_logic = self.air_x
        self.air_cp = (self.air_cph20*self.air_x+self.air_cpair)/(1+self.air_x)
        self.air_k_k_minus_one = self.air_rg / self.air_cp
        self.air_k = 1 / (1 - self.air_k_k_minus_one)
        self.air_rho_amb = self.air_p0*100000/(self.air_rg*(self.air_t0+KEL))
        self.air_amb_density = (self.air_t0+273.15) / 273.15 * (1 + self.air_x_logic) * 1.01325 / self.air_p0 * self.air_rg / RAIR

class FlowDefAir(MoistureAir):
    """
    initialize the definition of flow
    """
    def __init__(self, air_t0, air_rh, flow, air_p0 = 1.0133):
        super(FlowDefAir, self).__init__(air_t0, air_rh, air_p0)
        self.air_rho_inlet = self.air_p0 * 100000 / (self.air_rg * (self.air_t0 + KEL))
        self.air_flow = flow / self.air_amb_density

class RatedPointAir(MoistureAir):
    """
    initialize the attributes under rated condition
    """
    def __init__(self, air_t0, air_rh, inlet_press_loss, air_p0 = 0.988):
        super(RatedPointAir, self).__init__(air_t0, air_rh, air_p0)
        self.air_rho_inlet = (self.air_p0-inlet_press_loss)*100000/(self.air_rg*(self.air_t0+KEL))
        self.air_inlet_density = (self.air_t0+273.15)/273.15*(1+self.air_x_logic)*1.01325 \
                                 /(self.air_p0-inlet_press_loss)*self.air_rg/RAIR
        self.air_csound = (self.air_rg*self.air_k*(self.air_t0+KEL))**0.5

class DutyPointAir(MoistureAir):
    """
    initialize the attributes under different working condition
    air_rho_inlet and air_inlet_density should be updated later
    """
    def __init__(self, air_t0, air_rh, air_p0 = 0.988):
        super(DutyPointAir, self).__init__(air_t0, air_rh, air_p0)
        self.air_rho_inlet = 0.0
        self.air_inlet_density = 0.0
