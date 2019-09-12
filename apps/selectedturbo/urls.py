# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from .views import SelectView
from .views import ExcelView

app_name = "turbo"

urlpatterns = [
    path("selection/", SelectView.as_view(), name="selection"),
    path("excel/", ExcelView.as_view(), name="excel"),
]