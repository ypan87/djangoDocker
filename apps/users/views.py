import json
from functools import wraps

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm, LoginForm, ForgetForm, ModifyPwdForm
from .models import UserProfile, EmailVerifyRecord
from utils.email_send import send_register_email
from selectedturbo.services.const import LANGUAGE

def get_messages():
    return {
        "cn": {
            "resetLinkInvalid": "重置密码链接无效，请重新填写表格"
        },
        "en": {
            "resetLinkInvalid": "Reset password link is invalid. Please refill the form."
        }
    }

def get_lang_url(alias_name, kwargs):
    lang_urls = {
        LANGUAGE["en"]: reverse(alias_name, kwargs={**{"lang": LANGUAGE["en"]}, **kwargs}),
        LANGUAGE["cn"]: reverse(alias_name, kwargs={**{"lang": LANGUAGE["cn"]}, **kwargs})
    }
    return lang_urls

def guest_required(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("user_projects", kwargs={"user_id": request.user.id, "lang":LANGUAGE["en"]}))
        return func(view, request, *args, **kwargs)
    return wrapper

class EmailRegisterView(View):
    def get(self, request):
        return render(request, 'email_register.html')

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
        if not register_form.is_valid():
            if "captcha" in register_form.errors.keys():
                return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "CaptchaError"
                    }),
                    content_type="application/json"
                )
            # 获取所有错误
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError"
                }),
                content_type="application/json"
            )
        email = request.POST.get("email", "")
        pass_word = request.POST.get("password", "")

        user_record = UserProfile.objects.filter(email=email)
        if user_record:
            return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "EmailAlreadyExist"
                    }),
                    content_type="application/json"
                )

        # 实例化userProfile对象
        # 发送注册激活邮件
        try:
            send_register_email(email, host, "register")
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "EmailSendFail"
                }),
                content_type="application/json"
            )

        try:
            with transaction.atomic():
                user_profile = UserProfile()
                user_profile.username = email
                user_profile.email = email

                # 默认注册状态为false
                user_profile.is_active = False

                # 加密密码
                user_profile.password = make_password(pass_word)
                user_profile.save()

                # 发送成功注册消息
                messages.success(request, "Sign up successfully. Please check your email to activate your account.")
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "InternalError"
                }),
                content_type="application/json"
            )

        # 发送正确信息
        return HttpResponse(
                json.dumps({
                    "status": "success",
                    "url": reverse("login"),
                }),
                content_type="application/json"
        )
# 激活用户
class ActiveUserView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code, send_type="register")
        if not all_record:
            messages.error(request, "Your activate link is invalid")
            return HttpResponseRedirect(reverse("register"))
        record = all_record[0]
        email = record.email
        user = UserProfile.objects.get(email=email)
        user.is_active = True
        user.save()
        messages.success(request, "Activate successfully，please Log in")
        return render(request, "login.html")

class LoginView(View):
    @guest_required
    def get(self, request):
        next = ""
        if "next" in request.GET:
            next = request.GET["next"]

        return render(request, "login.html", {"next": next})

    @guest_required
    def post(self, request):
        login_form = LoginForm(request.POST)
        if not login_form.is_valid():
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError",
                }),
                content_type="application/json"
            )
        user_name = request.POST.get("email", "")
        pass_word = request.POST.get("password", "")
        user = authenticate(username=user_name, password=pass_word)

        if not user:
            return HttpResponse(json.dumps({
                "status": "failure",
                "errorCode": "PasswordIncorrect"
            }), content_type="application/json")

        if not user.is_active:
            return HttpResponse(json.dumps({
                "status": "failure",
                "errorCode": "UserNotActive",
            }), content_type="application/json")

        login(request, user)
        url = reverse("user_projects", kwargs={"user_id": user.id, "lang": LANGUAGE["en"]})
        redirect_url = request.GET.get('next', '')
        if redirect_url:
            url = redirect_url
        return HttpResponse(json.dumps({
            "status": "success",
            "url": url,
            "errorCode": ""
        }), content_type="application/json")

class ForgetPwdView(View):
    def get(self, request, lang="cn"):
        forget_form = ForgetForm()
        lang_urls = get_lang_url("forget_pwd", {})
        return render(request, "forget_pwd.html", {
            "forget_form": forget_form,
            "lang": lang,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

    def post(self, request, lang="cn"):
        host = request.get_host()
        forget_form = ForgetForm(request.POST)
        if not forget_form.is_valid():
            if "captcha" in forget_form.errors.keys():
                return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "CaptchaError"
                    }),
                    content_type="application/json"
                )
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError",
                }),
                content_type="application/json"
            )

        email = request.POST.get("email", "")

        try:
            send_register_email(email, host, "forget")
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "EmailSendFail"
                }),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps(
                {
                    "status": "success",
                    "errorCode": "",
                    "lang": lang,
                }
            ),
            content_type="application/json"
        )

class ResetView(View):
    def get(self, request, lang, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code, send_type="forget")
        if not all_record:
            messages.error(request, get_messages()[lang]["resetLinkInvalid"])
            return HttpResponseRedirect(reverse("forget_pwd", kwargs={"lang": lang}))

        email = all_record[0].email
        lang_urls = get_lang_url("reset_pwd", {"active_code": active_code})
        return render(
            request, "password_reset.html", {
                "lang": lang,
                "langCategory": LANGUAGE,
                "langUrls": lang_urls,
                "email": email,
            }
        )

class ModifyPwdView(View):
    def post(self, request, lang="cn"):
        modify_form = ModifyPwdForm(request.POST)
        if not modify_form.is_valid():
            return HttpResponse(json.dumps(
                {
                    "status": "failure",
                    "errorCode": "ParameterError",
                    "lang": lang,
                }
            ), content_type="application/json")
        pwd1 = request.POST.get("password1", "")
        pwd2 = request.POST.get("password2", "")
        email = request.POST.get("email", "")
        if pwd1 != pwd2:
            return HttpResponse(json.dumps(
                {
                    "status": "failure",
                    "errorCode": "PasswordNotEqual",
                    "lang": lang
                }
            ), content_type="application/json")
        user = UserProfile.objects.get(email=email)
        if not user:
            return HttpResponse(json.dumps(
                {
                    "status": "failure",
                    "errorCode": "UserNotExist",
                    "lang": lang,
                }
            ), content_type="application/json")

        user.password = make_password(pwd2)
        user.save()
        messages.success(request, "Update password successfully")
        url = reverse("login")
        return HttpResponse(json.dumps(
            {
                "status": "success",
                "errorCode": "",
                "lang": lang,
                "url": url,
            }
        ), content_type="application/json")

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