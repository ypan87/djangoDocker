/**
 * Created by yifan_pan on 2019/10/16.
 */
import {errorCode, Validation, toastrTime, language} from "./base";
import {DOMs, DOMstrings, URLs} from "../password_reset/views/passwordResetView";
import {Request, handleResponse, getLang} from "../util/util";

let validator = new Validation();
let lang = getLang();

validator.add(DOMs.resetPwdForm.password1, [
    {
        strategy: "password",
        errorMsg: {
            "en": "Password Format Incorrect",
            "cn": "密码格式错误",
        }
    }
]);

validator.add(DOMs.resetPwdForm.password2, [
    {
        strategy: "password",
        errorMsg: {
            "en": "Password Format Incorrect",
            "cn": "密码格式错误",
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
    let result = true;
    if (!checkPasswordConsistency()) result = false;
    let results = validator.start();
    if(results.length != 0) {
        result = false;
        for (let i = 0, result; result = results[i++];) {
            if (result.msg) {
                displayError.call(result.dom, result.msg);
            }
        }
    }

    return result;
};

const checkPasswordConsistency = function() {
    if (DOMs.resetPwdForm.password1.value != DOMs.resetPwdForm.password2.value) {
        displayError.call(DOMs.resetPwdForm.password2, {
            "en": "Password Format Incorrect",
            "cn": "密码格式错误",
        });
        return false;
    }
    return true;
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

const sendResetRequest = async function() {
    var formData = $(`#${DOMstrings.resetPwdForm}`).serialize();
    var url = "/" + lang + URLs.resetPwd;
    let request = new Request(url, formData);

    try {
        await request.getResults();
        handleResponse(request.data, "ResetPwdSuccess", lang);
    } catch (err) {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["NetworkError"]
        );
    }
};

// add event listener
DOMs.resetPwdBtn.addEventListener("click", function(event) {
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
    sendResetRequest();
});

DOMs.resetPwdForm.addEventListener("blur", function(event) {
    if (!event.target.matches("input")) {return false;}
    if (event.target.value == "") {
        var error = event.target.parentElement.nextElementSibling;
        error.className = "forget-pwd-require-error";
        if (event.target.id == "password1") {
            error.innerHTML = language[lang]["password1NonEmpty"];
        } else if (event.target.id == "password2") {
            error.innerHTML = language[lang]["password2NonEmpty"];
        }
    }
}, true);

DOMs.resetPwdForm.addEventListener("focus", function(event) {
    if (!event.target.matches("input")) {return false;}
    var error = event.target.parentElement.nextElementSibling;
    if (!error.classList.contains("hidden")) {
        error.innerHTML = "";
        error.classList.add("hidden");
    }
}, true);

DOMs.password1Error.addEventListener("click", errorClickEvent);
DOMs.password2Error.addEventListener("click", errorClickEvent);

// initialize tooltip

$('#password1').tooltip({
    title: language[lang]["passwordTip"]
});

