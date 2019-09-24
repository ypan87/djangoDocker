# !/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from users.models import UserProfile

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

# 项目信息
class Project(models.Model):
    project_name = models.CharField(default="", max_length=100, verbose_name=u"项目名称")
    project_index = models.CharField(default="", max_length=100, verbose_name=u"项目编号")
    project_address = models.CharField(default="", max_length=100, verbose_name=u"项目地址")
    project_engineer = models.CharField(default="", max_length=100, verbose_name=u"项目工程师")
    creator = models.ForeignKey("users.UserProfile", on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=datetime.now, verbose_name=u"创建时间")

# 选型信息
class Sizer(models.Model):
    FREQUENCY_CHOICES = [
        ("50", "50HZ"),
        ("60", "60HZ")
    ]
    creator = models.ForeignKey("users.UserProfile", on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    update_time = models.DateTimeField(default=datetime.now, verbose_name=u"修改时间")
    is_imperial = models.BooleanField(default=False)
    altitude = models.FloatField(default=0)
    inlet_press = models.FloatField(default=0)
    frequency_select = models.CharField(default="50", choices=FREQUENCY_CHOICES, max_length=100)
    units_num = models.IntegerField(default=1)
    volt = models.IntegerField(default=400)
    material = models.CharField(default="ALU", max_length=30)
    safety_factor = models.FloatField(default=1)
    ei_rating = models.FloatField(default=3)
    env_temp = models.FloatField(default=0)
    rating_flow = models.FloatField(default=0)
    rating_pressure = models.FloatField(default=0)
    rating_temp = models.FloatField(default=0)
    rating_humi = models.FloatField(default=0)
    rating_point_inlet_pressure = models.FloatField(default=0)
    rating_point_inlet_temp = models.FloatField(default=0)
    rating_point_humi = models.FloatField(default=0)
    rating_point_inlet_loss = models.FloatField(default=0)
    rating_point_outlet_loss = models.FloatField(default=0)
    rating_point_out_pressure = models.FloatField(default=0)
    max_flow_coeff = models.FloatField(default=0)
    max_pressure_coeff = models.FloatField(default=0)
    working_conditions = models.TextField(default="")
