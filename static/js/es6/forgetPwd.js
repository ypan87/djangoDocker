/**
 * Created by yifan_pan on 2019/10/16.
 */
import {errorCode, Validation, toastrTime, language} from "./base";
import {DOMs, DOMstrings, URLs} from "../forgetPwd/views/forgetPwdView";
import {Request, handleResponse, getLang} from "../util/util";

let validator = new Validation();
let lang = getLang();

validator.add(DOMs.forgetPwdForm.email, [
    {
        strategy: 'isNonEmpty',
        errorMsg: {
            "en": "Input Value Required",
            "cn": "输入值不能为空"
        },
    },
    {
        strategy: "email",
        errorMsg: {
            "en": "Email Format Incorrect",
            "cn": "邮箱格式错误"
        }
    }

]);

const displayError = function(errorMsg) {
    let inputError = this.parentElement.nextElementSibling;
    if (!inputError) return;
    inputError.className = "forget-pwd-common-error";
    inputError.innerHTML = errorMsg[lang];
};

const validateFields = function() {
    var results = validator.start();
    if(results.length == 0) {
        return true;
    }
    for (let i = 0, result; result = results[i++];) {
        if (result.msg) {
            displayError.call(result.dom, result.msg);
        }
    }
    return false;
};

const errorClickEvent = function() {
    this.innerHTML="";
    this.classList.add("hidden");
    let input = this.previousElementSibling.firstElementChild;
    if (this.id == "captchaError") {
        input = this.previousElementSibling.lastElementChild;
    }
    input.focus();
};

const sendForgetRequest = async function() {
    var formData = $(`#${DOMstrings.forgetPwdForm}`).serialize();
    var url = "/" + lang + URLs.forgetPwd;
    let request = new Request(url, formData);
    try {
        await request.getResults();
        handleResponse(request.data, "findPwdSuccess", lang);
        if (request.data.status == "failure") {
            refreshCaptcha();
        }
    } catch (err) {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["NetworkError"]
        );
        refreshCaptcha();
    }
};

// add event listener
DOMs.forgetPwdBtn.addEventListener("click", function(event) {
    if (!validateFields()) {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            "Parameters Wrong, Please Correct"
        );
        return false;
    }
    sendForgetRequest();
});

DOMs.forgetPwdForm.addEventListener("blur", function(event) {
    if (!event.target.matches("input")) {return false;}
    if (event.target.value == "") {
        var error = event.target.parentElement.nextElementSibling;
        error.className = "forget-pwd-require-error";
        if (event.target.id == "email") {
            error.innerHTML = language[lang]["emailNonEmpty"];
        } else if (event.target.id == "id_captcha_1") {
            error.innerHTML = language[lang]["captchaNonEmpty"];
        }
    }
}, true);

DOMs.forgetPwdForm.addEventListener("focus", function(event) {
    if (!event.target.matches("input")) {return false;}
    var error = event.target.parentElement.nextElementSibling;
    if (!error.classList.contains("hidden")) {
        error.innerHTML = "";
        error.classList.add("hidden");
    }
}, true);

DOMs.emailError.addEventListener("click", errorClickEvent);
DOMs.captchaError.addEventListener("click", errorClickEvent);

// setup captcha
const setupCaptcha = function() {
    DOMs.captcha.placeholder = language[lang]["captcha"];

    $('.captcha').click(function () {
        refreshCaptcha();
    });
};

// refresh captcha
const refreshCaptcha = function() {
    $.getJSON("/captcha/refresh/", function (result) {
        $('.captcha').attr('src', result['image_url']);
        $('#id_captcha_0').val(result['key']);
    });
};

setupCaptcha();