# !/usr/bin/python
# -*- coding: utf-8 -*-
import json

def form_validation_errors(form):
    json_errors = {"status": "error"}
    for key, value in form.errors.items():
        json_errors[key] = value[0]
    return json.dumps(json_errors)