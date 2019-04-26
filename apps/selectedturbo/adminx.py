# !/usr/bin/python
# -*- coding: utf-8 -*-

from .models import TestPoints, Turbo
import xadmin

class TurboAdmin(object):
    list_display = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]
    search_fields = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]
    list_filter = ["category", "cut_back", "diameter", "fix_loss_one", "fix_loss_two", "var_loss", "size_correction"]

class TestPointsAdmin(object):
    list_display = ["category", "working_condition", "working_position", "flow_coef", "pressure_coef", "efficiency", "flow_factor", "pressure_factor", "efficiency_factor"]
    search_fields = ["category", "working_condition", "working_position", "flow_coef", "pressure_coef", "efficiency", "flow_factor", "pressure_factor", "efficiency_factor"]
    list_filter = ["category", "working_condition", "working_position", "flow_coef", "pressure_coef", "efficiency", "flow_factor", "pressure_factor", "efficiency_factor"]

xadmin.site.register(TestPoints, TestPointsAdmin)
xadmin.site.register(Turbo, TurboAdmin)