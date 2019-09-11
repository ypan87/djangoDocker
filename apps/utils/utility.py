# !/usr/bin/python
# -*- coding: utf-8 -*-

from selectedturbo.services.const import *

# 英制压力单位转换为公制
def imperial_pressure_to_metric(value):
    return value / PSI

# 将英制温度转换为公制温度
def imperial_temp_to_metric(value):
    return (value - FB) / FA

# 将英制流量转换为公制流量
def imperial_flow_to_metric(value):
    return value * ACFM

# 将英制长度转换为公制长度
def imperial_length_to_metric(value):
    return value / FEET

def imperial_metric_value_to_metric(value, is_imperial, unit):
    if not is_imperial:
        return value
    if unit == LENGTH:
        return imperial_length_to_metric(value)
    elif unit == FLOW:
        return imperial_flow_to_metric(value)
    elif unit == TEMP:
        return imperial_temp_to_metric(value)
    elif unit == PRES:
        return imperial_pressure_to_metric(value)
    else:
        return value