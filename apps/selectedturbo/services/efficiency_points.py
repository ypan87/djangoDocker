# !/usr/bin/python
# -*- coding: utf-8 -*-

class EfficiencyPoint(object):

    def __init__(self, efficiency, flow_coeff, pressure_coeff):
        self.efficiency = efficiency
        self.flow_coeff = flow_coeff
        self.pressure_coeff = pressure_coeff