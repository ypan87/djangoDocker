# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from .views import CreateProjectView
from .views import GetUserProjectsView

app_name = "users"

urlpatterns = [
    path("<int:user_id>/projects/create/", CreateProjectView.as_view(), name="create_project"),
    path("<int:user_id>/projects/", GetUserProjectsView.as_view(), name="user_projects"),
]