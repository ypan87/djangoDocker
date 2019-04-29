# !/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models

# 鼓风机型号
TURBO_CHOICES = [
    ("GL1", u"GL1"),
    ("GL2", u"GL2"),
    ("GL3", u"GL3"),
    ("GL5", u"GL5"),
    ("GL8", u"GL8"),
    ("GL10", u"GL10"),
    ("GL15", u"GL15"),
    ("GL20", u"GL20"),
    ("GL30", u"GL30"),
    ("GL50", u"GL50"),
]

class Turbo(models.Model):
    category = models.CharField(max_length=10, verbose_name=u"鼓风机型号", choices=TURBO_CHOICES, default="GL1")
    cut_back = models.FloatField(verbose_name=u"cut back")
    diameter = models.FloatField(verbose_name=u"直径")
    fix_loss_one = models.FloatField(verbose_name=u"fix loss one")
    fix_loss_two = models.FloatField(verbose_name=u"fix loss two")
    var_loss = models.FloatField(verbose_name=u"var loss")
    size_correction = models.FloatField(verbose_name=u"size correction")

    class Meta:
       verbose_name = "鼓风机"
       verbose_name_plural = verbose_name

    def __str__(self):
        return "鼓风机：" + self.category + "，cut back：" + str(self.cut_back)

# 测试工况点
class TestPoints(models.Model):
    category = models.CharField(max_length=10, verbose_name=u"鼓风机型号", choices=TURBO_CHOICES, default="GL3")
    working_condition = models.IntegerField(default=0, verbose_name=u"工况")
    working_position = models.IntegerField(default=0, verbose_name=u"工况点")
    flow_coef = models.FloatField(verbose_name=u"流量系数")
    pressure_coef = models.FloatField(verbose_name=u"压力系数")
    efficiency = models.FloatField(verbose_name=u"效率")
    flow_factor = models.FloatField(verbose_name=u"流量因子")
    pressure_factor = models.FloatField(verbose_name=u"压力因子")
    efficiency_factor = models.FloatField(verbose_name=u"效率因子")

    class Meta:
        verbose_name = "工况点"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "鼓风机：" + self.category + "，工况：" + str(self.working_condition) + "，工况点：" + str(self.working_position)
