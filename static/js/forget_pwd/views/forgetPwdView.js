/**
 * Created by yifan_pan on 2019/10/16.
 */
export const DOMs = {
    emailError: document.getElementById("emailError"),
    captchaError: document.getElementById("captchaError"),
    forgetPwdForm: document.getElementById("forgetPwdForm"),
    email: document.getElementById("email"),
    captcha: document.getElementById("id_captcha_1"),
    forgetPwdBtn: document.getElementsByClassName("forget-pwd-submit-button")[0],
    loadIcon: document.querySelector('.overlay'),
};

export const URLs = {
    forgetPwd: "/forget/"
};

export const DOMstrings = {
    forgetPwdForm: "forgetPwdForm"
};
