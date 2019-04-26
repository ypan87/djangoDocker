# !/usr/bin/python
# -*- coding: utf-8 -*-

from .air import FlowDefAir

class Project(object):

    def __init__(self, max_flow_coef, pressure_coef, altitude=0, inlet_pressure=0.988, grid_freq=50,
                 num=0, volt=400, mat="ALU", safe_coef=1, ei_rating=3,
                 amb_temp=45, stand_flow=3486.0, stand_pressure=1.0133,
                 stand_temp=20, stand_rh=70):
        """
        Initialize the basic info of a project
        All the default arguments are listed as below:

        altitude        Altitude of the project
        inlet_pressure  Inlet_pressure of the turbo
        grid_freq       Grid frequency of the project
        num             Number of the turbo units
        volt            Volt of the project
        mat             material of the turbo
        safe_coef       safe coefficient of the project
        ei_rating       ei_rating of the project
        amb_temp        ambient temperature of the project
        stand_flow      rating flow of turbo
        stand_pressure  rating pressure of the turbo
        stand_temp      rating temperature of the turbo
        stand_rh        rating relative humidity
        """
        self.altitude = altitude
        self.inlet_pressure = inlet_pressure
        self.grid_freq = grid_freq
        self.num = num
        self.volt = volt
        self.mat = mat
        self.safe_coef = safe_coef
        self.ei_rating = ei_rating
        self.amb_temp = amb_temp
        self.stand_flow = stand_flow
        self.stand_pressure = stand_pressure
        self.round_pressure = round(self.stand_pressure, 4)
        self.stand_temp = stand_temp
        self.stand_rh = stand_rh
        self.max_flow_coef = max_flow_coef
        self.pressure_coef = pressure_coef
        self.air_cond = FlowDefAir(stand_temp, stand_rh, stand_flow, self.round_pressure)