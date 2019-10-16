/**
 * Created by yifan_pan on 2019/10/16.
 */
import {errorCode, Validation, toastrTime} from "./base";
import {DOMs, DOMstrings, URLs} from "../login/views/loginView"
import {Request, handleResponse} from "../util/util";

let validator = new Validation();

validator.add(DOMs.loginForm.email, [{
    strategy: 'isNonEmpty',
    errorMsg: "Input Value Required",
}]);

validator.add(DOMs.loginForm.password, [
    {
        strategy: "isNonEmpty",
        errorMsg: "Input Value Required",
    },

    {
        strategy: "minLength:6",
        errorMsg: "At Least 6 Characters Required"
    },

    {
        strategy: "maxLength:20",
        errorMsg: "Password Too Long"
    }
]);

const displayError = function(errorMsg) {
    let inputError = this.parentElement.nextElementSibling;
    if (!inputError) return;
    inputError.className = "register-login-common-error";
    inputError.innerHTML = errorMsg;
};

const validateFields = function() {
    let results = validator.start();
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
    input.focus();
};

// send login request
const sendLoginRequest = async function() {
    let formData = $(`#${DOMstrings.loginForm}`).serialize();
    let url = URLs.login + "/?next=" + this.dataset.url;
    let request = new Request(url, formData);

    try {
        await request.getResults();
        handleResponse(request.data, "loginSuccess")
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

// setup event listeners
DOMs.switchBtn.addEventListener("click", function(event) {
    location.href = URLs.register;
});

DOMs.forgetPwdBtn.addEventListener("click", function(event) {
    window.open(URLs.forget, "_blank");
});

DOMs.loginBtn.addEventListener("click", function(event) {
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
    sendLoginRequest.call(this);
});

// focus blur event not gonna bubble up, need another parameter "true"
DOMs.loginForm.addEventListener("blur", function(event) {
    if (!event.target.matches("input")) {return false;}
    if (event.target.value == "") {
        let error = event.target.parentElement.nextElementSibling;
        error.className = "register-login-require-error";
        if (event.target.id == "email") {
            error.innerHTML = "Please Input Email";
        } else if (event.target.id == "password") {
            error.innerHTML = "Please Input Password";
        }
    }
}, true);

DOMs.loginForm.addEventListener("focus", function(event) {
    if (!event.target.matches("input")) {return false;}
    let error = event.target.parentElement.nextElementSibling;
    if (!error.classList.contains("hidden")) {
        error.innerHTML = "";
        error.classList.add("hidden");
    }
}, true);

DOMs.emailError.addEventListener("click", errorClickEvent);
DOMs.passwordError.addEventListener("click", errorClickEvent);