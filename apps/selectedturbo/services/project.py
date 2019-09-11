# !/usr/bin/python
# -*- coding: utf-8 -*-

from .air import FlowDefAir
from utils.utility import *

class Project(object):

    def __init__(self, name, serial_num, location, max_flow_coef, pressure_coef, turbo_list,
                 altitude=0, is_imperial=False, is_wet=False, inlet_pressure=0.988, grid_freq=50,
                 num=0, volt=400, mat="ALU", safe_coef=1, ei_rating=3, amb_temp=45,
                 stand_flow=3486.0, stand_pressure=1.0133, stand_temp=20, stand_rh=70):
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
        self.name = name
        self.serial_num = serial_num
        self.altitude = altitude
        self.location = location
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
        self.stand_temp = stand_temp
        self.stand_rh = stand_rh
        self.max_flow_coef = max_flow_coef
        self.pressure_coef = pressure_coef
        self.is_wet = is_wet
        self.is_imperial = is_imperial
        self.turbo_list = turbo_list
        self.final_altitude = self.final_amb_temp = self.final_stand_flow = self.final_stand_pressure = None
        self.final_stand_temp = self.final_stand_rh = self.air_cond = self.de_rating = None
        self.selected_turbo = self.cut_back_width = None
        self.gear_loss_fix = self.gear_loss_var = None
        self.initialize_none_variables()

    def initialize_none_variables(self):
        self.final_altitude = imperial_metric_value_to_metric(self.altitude, self.is_imperial, LENGTH)
        self.final_amb_temp = round(imperial_metric_value_to_metric(self.amb_temp, self.is_imperial, TEMP), 2)
        self.final_stand_flow = imperial_metric_value_to_metric(self.stand_flow, self.is_imperial, FLOW)
        self.final_stand_pressure = round(imperial_metric_value_to_metric(self.stand_pressure, self.is_imperial, PRES), 4)
        self.final_stand_temp = imperial_metric_value_to_metric(self.stand_temp, self.is_imperial, TEMP)
        self.final_stand_rh = self.stand_rh
        # 创建project对应的air数据并初始化可以计算的数据
        self.air_cond = FlowDefAir(self.final_stand_temp, self.final_stand_rh, self.final_stand_flow, self.is_wet, self.final_stand_pressure)
        self.calculate_de_rating()

    def calculate_de_rating(self):
        self.de_rating = 1 if self.final_amb_temp <= 45 else (155-self.final_amb_temp)/110
