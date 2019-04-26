import json
from django.shortcuts import render
from django.views.generic import View
from .forms import RegisterForm, LoginForm, ActiveForm, ForgetForm, ModifyPwdForm
from .models import UserProfile, EmailVerifyRecord
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from functools import wraps


def guest_required(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return func(view, request, *args, **kwargs)
    return wrapper


class LogoutView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("login"))


class RegisterView(View):
    @guest_required
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html',
                      {'register_form': register_form})

    @guest_required
    def post(self, request):
        register_form = RegisterForm(request.POST)
        # 获取host
        host = request.get_host()
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            pass_word = request.POST.get("password", "")

            # 实例化userProfile对象
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name

            # 默认注册状态为false
            user_profile.is_active = False

            # 加密密码
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 发送注册激活邮件
            send_register_email(user_name, host, "register")

            # 发送成功注册消息
            messages.success(request, '注册成功，请前往邮箱激活账户，邮件可能会被放入垃圾邮件中')

            # 发送正确信息
            return HttpResponse(
                    json.dumps({
                        "status": "ok",
                    }),
                    content_type="application/json"
            )
        else:
            # 获取所有错误
            return HttpResponse(
                form_validation_errors(register_form),
                content_type="application/json"
            )


# 激活用户
class ActiveUserView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code, send_type="register")
        if all_record:
            for record in all_record:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            messages.error(request, "您的激活链接无效")
            return HttpResponseRedirect(reverse("register"))
        messages.success(request, "账号激活成功，请登录账户")
        return render(request, "login.html")


class LoginView(View):
    @guest_required
    def get(self, request):
        return render(request, "login.html", {})

    @guest_required
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("email", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            # TODO next 获取
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse(json.dumps({
                        "status": "ok"
                    }), content_type="application/json")
                else:
                    return HttpResponse(json.dumps({
                        "status": "error",
                        "email": "用户尚未激活，请前往邮箱激活"
                    }), content_type="application/json")
            else:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "password": "密码错误"
                }), content_type="application/json")
        else:
            return HttpResponse(
                form_validation_errors(login_form),
                content_type="application/json"
            )


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forget_pwd.html", {"forget_form": forget_form})

    def post(self, request):
        host = request.get_host()
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_register_email(email, host, "forget")
            return HttpResponse(
                json.dumps({"status": "ok"}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                form_validation_errors(forget_form),
                content_type="application/json"
            )



class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')



class ResetView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code, send_type="forget")
        if all_record:
            for record in all_record:
                email = record.email
                return render(
                    request, "password_reset.html", {
                        "email": email,
                    }
                )
        else:
            messages.error(request, '您的重置密码链接无效，请重新请求')
            return HttpResponseRedirect(reverse("forget_pwd"))


class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return HttpResponse(json.dumps({
                    "status": "error",
                    "password2": "密码不一致"
                }), content_type="application/json")
            user = UserProfile.objects.get(email=email)
            if user:
                user.password = make_password(pwd2)
                user.save()
                messages.success(request, "密码重置成功")
                return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
            else:
                messages.error(request, "用户不存在，请重新请求")
                return HttpResponse(json.dumps({"status": "error", "user":"用户不存在"}))
        else:
            return HttpResponse(
                form_validation_errors(modify_form),
                content_type="application/json"
            )


def form_validation_errors(form):
    json_errors = {"status": "error"}
    for key, value in form.errors.items():
        json_errors[key] = value[0]
    return json.dumps(json_errors)


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(
                Q(username=username) |
                Q(email=username)
            )
            if user.check_password(password):
                return user
        except Exception as e:
            return None