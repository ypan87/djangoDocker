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
from selectedturbo.views import GetAllProjectsView, CreateSizerView, ProjectView, CheckBlowerView, ExcelView, \
     SizerView, EditSizerView, EditProjectView, CreateProjectView, GetUserProjectsView, DeleteSizerView, DeleteProjectView

import xadmin

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    path("captcha/", include('captcha.urls')),
    path("active/<str:active_code>/", ActiveUserView.as_view(), name="user_active"),
    path("<str:lang>/forget/", ForgetPwdView.as_view(), name="forget_pwd"),
    path("<str:lang>/reset/<str:active_code>", ResetView.as_view(), name="reset_pwd"),
    path("<str:lang>/modify_pwd/<str:active_code>/", ModifyPwdView.as_view(), name="modify_pwd"),
    path("email_register/", EmailRegisterView.as_view()),
    path("<str:lang>/projects/", GetAllProjectsView.as_view(), name="all_projects"),
    path("<str:lang>/projects/<int:project_id>/", ProjectView.as_view(), name="project"),
    path("<str:lang>/projects/<int:project_id>/edit/", EditProjectView.as_view(), name="project_edit"),
    path("<str:lang>/projects/<int:project_id>/delete/", DeleteProjectView.as_view(), name="project_delete"),
    path("<str:lang>/projects/sizers/check/", CheckBlowerView.as_view(), name="check_blower"),
    path("<str:lang>/projects/sizers/excel/", ExcelView.as_view(), name="excel"),
    path("<str:lang>/users/<int:user_id>/projects/create/", CreateProjectView.as_view(), name="create_project"),
    path("<str:lang>/users/<int:user_id>/projects/", GetUserProjectsView.as_view(), name="user_projects"),
    path("<str:lang>/sizers/<int:sizer_id>/", SizerView.as_view(), name="sizer"),
    path("<str:lang>/sizers/<int:sizer_id>/edit/", EditSizerView.as_view(), name="sizer_edit"),
    path("<str:lang>/projects/<int:project_id>/sizer/create/", CreateSizerView.as_view(), name="sizer_create"),
    path("<str:lang>/sizers/<int:sizer_id>/delete/", DeleteSizerView.as_view(), name="sizer_delete"),
]
