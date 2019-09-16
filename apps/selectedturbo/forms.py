# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django import forms

class SelectionForm(forms.Form):
    LANG_CHOICES = [
        ("cn", "中文"),
        ("en", "English")
    ]
    UNIT_CHOICES = [
        ("metric", "公制/metric"),
        ("imperial", "英制/imperial")
    ]
    FREQUENCY_CHOICES = [
        ("50", "50HZ"),
        ("60", "60HZ")
    ]
    langSelect = forms.ChoiceField(required=True, choices=LANG_CHOICES)
    isImperial = forms.ChoiceField(required=True, choices=UNIT_CHOICES)
    projectName = forms.CharField(required=False, max_length=30, error_messages={"max_length": "输入值不能超过30个字符"})
    projectNumber = forms.CharField(required=False, max_length=30, error_messages={"max_length": "输入值不能超过30个字符"})
    projectLocation = forms.CharField(required=False, max_length=30, error_messages={"max_length": "输入值不能超过30个字符"})
    projectEngineer = forms.CharField(required=False)
    projectAltitude = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    # projectEnvPres = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    projectInletPres = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    frequencySelect = forms.ChoiceField(required=True, choices=FREQUENCY_CHOICES)
    projectUnitsNum = forms.IntegerField(required=True, min_value=0, error_messages={"min_value": "请输入大于0的整数"})
    projectVolt = forms.IntegerField(required=True, min_value=0, error_messages={"min_value": "请输入大于0的整数"})
    projectMaterial = forms.CharField(required=False, max_length=30, error_messages={"max_length": "输入值不能超过30个字符"})
    projectSafetyFactor = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    projectEIRating = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    projectEnvTemp = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingFlow = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPressure = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingTemp = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingHumi = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointInletPressure = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointInletTmep = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointHumi = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointInletLoss = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointOutletLoss = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    ratingPointOutPressure = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    maxFlowCoeff = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    maxPressureCoeff = forms.FloatField(required=True, error_messages={"required": "输入值不能为空"})
    workingConditions = forms.CharField(required=True, error_messages={"required": "输入值不能为空"})

    def clean_workingConditions(self):
        data = self.cleaned_data["workingConditions"]
        return json.loads(data)


