# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module contains the TurboData class, which represents the detail stats of every turbo
"""
from selectedturbo.models import Turbo

class TurboData(object):
    def __init__(self, turbo=None):
        self.coeff = 0.0
        self.val = 0
        x = isinstance(turbo, Turbo)
        self.type = turbo.category if x else "initial"
        self.cut_back = turbo.cut_back if x else 0
        self.d2 = turbo.diameter if x else 0
        self.fix_loss_1 = turbo.fix_loss_one if x else 0
        self.fix_loss_2 = turbo.fix_loss_two if x else 0
        self.var_loss = turbo.var_loss if x else 0
        self.size_correction = turbo.size_correction if x else 0