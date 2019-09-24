"""turboselection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include
from users.views import RegisterView, LoginView, LogoutView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, EmailRegisterView
from selectedturbo.views import GetAllProjectsView, CreateSizerView, ProjectView, CheckBlowerView, ExcelView, GetGraphDataView, SizerView, EditSizerView, EditProjectView

import xadmin

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('users/', include('selectedturbo.urls', namespace="users")),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    path("captcha/", include('captcha.urls')),
    path("active/<str:active_code>/", ActiveUserView.as_view(), name="user_active"),
    path("forget/", ForgetPwdView.as_view(), name="forget_pwd"),
    path("reset/<str:active_code>", ResetView.as_view(), name="reset_pwd"),
    path("modify_pwd/", ModifyPwdView.as_view(), name="modify_pwd"),
    path("email_register/", EmailRegisterView.as_view()),
    path("projects/", GetAllProjectsView.as_view(), name="all_projects"),
    path("projects/<int:project_id>/sizer/create/", CreateSizerView.as_view(), name="sizer_create"),
    path("projects/<int:project_id>/", ProjectView.as_view(), name="project"),
    path("projects/<int:project_id>/edit", EditProjectView.as_view(), name="project_edit"),
    path("projects/sizers/check/", CheckBlowerView.as_view(), name="check_blower"),
    path("projects/sizers/excel/", ExcelView.as_view(), name="excel"),
    path("projects/sizers/graph/", GetGraphDataView.as_view(), name="get_graph"),
    path("sizers/<int:sizer_id>/", SizerView.as_view(), name="sizer"),
    path("sizers/<int:sizer_id>/edit/", EditSizerView.as_view(), name="sizer_edit")
]
