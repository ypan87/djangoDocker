/**
 * Created by yifan_pan on 2019/10/16.
 */
import {errorCode, Validation, toastrTime} from "./base";
import {DOMs, DOMstrings, URLs} from "../register/views/registerView";
import {Request, handleResponse, disableBtn, ableBtn} from "../util/util";

let validator = new Validation();

validator.add(DOMs.registerForm.email, [
    {
        strategy: 'isNonEmpty',
        errorMsg: "Input Value Required",
    },
    {
        strategy: "email",
        errorMsg: "Email Format Wrong",
    },
]);

validator.add(DOMs.registerForm.password, [
    {
        strategy: "password",
        errorMsg: "Password Format Incorrect"
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
    if (this.id == "captchaError") {
        input = this.previousElementSibling.lastElementChild;
    }
    input.focus();
};

const renderLoading = function() {
    let markup = `
        <div class="loading">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    DOMs.registerBtn.textContent = "";
    DOMs.registerBtn.insertAdjacentHTML("afterbegin", markup);
};

const removeLoading = function(text) {
    DOMs.registerBtn.innerHTML = text;
};

// send register request
const sendRegisterRequest = async function() {
    let formData = $(`#${DOMstrings.registerForm}`).serialize();
    let url = URLs.register;
    let request = new Request(url, formData);
    try {
        await request.getResults();
        handleResponse(request.data, "registerSuccess");
        if (request.data.status == "failure") {
            refreshCaptcha();
        }
    } catch (err) {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode["en"]["NetworkError"]
        );
        refreshCaptcha();
    }
    ableBtn(DOMs.registerBtn);
    removeLoading("SignUp");
};

// add event listener
DOMs.switchBtn.addEventListener("click", function(event) {
    window.location.href = URLs.login;
});

DOMs.registerForm.addEventListener("blur", function(event) {
    if (!event.target.matches("input")) {return false;}
    if (event.target.value == "") {
        let error = event.target.parentElement.nextElementSibling;
        error.className = "register-login-require-error";
        if (event.target.id == "email") {
            error.innerHTML = "Please Input Email";
        } else if (event.target.id == "password") {
            error.innerHTML = "Please Input Password";
        } else if (event.target.id == "id_captcha_1") {
            error.innerHTML = "Please Input Captcha";
        }
    }
}, true);

DOMs.registerForm.addEventListener("focus", function(event) {
    if (!event.target.matches("input")) {return false;}
    let error = event.target.parentElement.nextElementSibling;
    if (!error.classList.contains("hidden")) {
        error.innerHTML = "";
        error.classList.add("hidden");
    }
}, true);

DOMs.registerBtn.addEventListener("click", function(event) {
    disableBtn(DOMs.registerBtn);
    renderLoading();
    if (!validateFields()) {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            "Parameters Wrong, Please Correct"
        );
        ableBtn(DOMs.registerBtn);
        removeLoading("SignUp");
        return false;
    }
    sendRegisterRequest();
});

DOMs.emailError.addEventListener("click", errorClickEvent);
DOMs.passwordError.addEventListener("click", errorClickEvent);
DOMs.captchaError.addEventListener("click", errorClickEvent);

// set up captcha
const setupCaptcha = function() {
    DOMs.captcha.placeholder = "Captcha";

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

