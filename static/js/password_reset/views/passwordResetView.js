/**
 * Created by yifan_pan on 2019/10/16.
 */

export const DOMs = {
    password2Error: document.getElementById("password2Error"),
    password1Error: document.getElementById("password1Error"),
    resetPwdForm: document.getElementById("pwdResetForm"),
    code: document.getElementById("code"),
    resetPwdBtn: document.getElementsByClassName("forget-pwd-submit-button")[0],
    loadIcon: document.querySelector('.overlay'),
};

export const URLs = {
    resetPwd: "/modify_pwd/"
};

export const DOMstrings = {
    resetPwdForm: "pwdResetForm"
};
