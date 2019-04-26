# !/usr/bin/python
# -*- coding: utf-8 -*-
import re
from users.models import UserProfile
from captcha.fields import CaptchaField
from django import forms
from django.db.models import Q

class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            # 用户未注册
            if not UserProfile.objects.filter(email=email) and not UserProfile.objects.filter(username=email):
                raise forms.ValidationError("该用户还未注册")



class RegisterForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={"required": "邮箱不能为空"})
    password = forms.CharField(required=True, min_length=6, max_length=20, error_messages={
        "required": "密码不能为空", "min_length": "密码长度不足", "max_length": "密码长度过长"})
    captcha = CaptchaField(error_messages={"invalid": "验证码错误", "required":"验证码不能为空"})

    def clean_password(self):
        password = self.cleaned_data["password"]
        if password:
            regex_password = u"^[0-9a-zA-Z_-]{6,20}$"
            p = re.compile(regex_password)
            if not p.match(password):
                raise forms.ValidationError("密码格式错误", code="passwordInvalid")


    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            if UserProfile.objects.filter(email=email):
                raise forms.ValidationError("邮箱已经被注册", code="userExist")


class ActiveForm(forms.Form):
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=6, max_length=20,error_messages={
        "required": "密码不能为空", "min_length": "密码长度不足", "max_length": "密码长度过长"})
    password2 = forms.CharField(required=True,error_messages={"required": "密码不能为空"})

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        if password:
            regex_password = u"^[0-9a-zA-Z_-]{6,20}$"
            p = re.compile(regex_password)
            if not p.match(password):
                raise forms.ValidationError("密码格式错误", code="passwordInvalid")

