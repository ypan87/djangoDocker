# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from .views import SelectView

app_name = "turbo"

urlpatterns = [
    path("selection/", SelectView.as_view(), name="selection")
]