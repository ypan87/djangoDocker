# !/usr/bin/python
# -*- coding: utf-8 -*-
from random import Random
from users.models import EmailVerifyRecord
from django.core.mail import send_mail, EmailMessage
from turboselection.settings import EMAIL_FROM
from django.template import loader

# 生成随机字符串
def random_str(random_length=8):
    str = ""
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str

def send_register_email(email, host, send_type="register", lang="en"):
    if send_type != "register" \
            and send_type != "forget" \
            and send_type != "update_email":
        return

    email_record = EmailVerifyRecord()
    if send_type == "update_email":
        code = random_str(4)
    else:
        code = random_str(16)

    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type

    email_record.save()

    # 定义邮件内容
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "GL-TURBO Activate Link"
        email_body = loader.render_to_string(
            "email_register.html",
            {
                "active_code": code,
                "host": host
            }
        )
    elif send_type == "forget":
        email_title = "GL-TURBO Reset Password"
        email_body = loader.render_to_string(
            "email_forget.html",
            {
                "active_code": code,
                "host": host,
                "lang": lang,
            }
        )
    elif send_type == "update_email":
        email_title = "GL-TURBO Update Email"
        email_body = loader.render_to_string(
            "email_update_email.html",
            {
                "active_code": code,
                "host": host
            }
        )

    msg = EmailMessage(email_title, email_body, EMAIL_FROM, [email])
    msg.content_subtype = "html"
    send_status = msg.send()

    if send_status:
        pass