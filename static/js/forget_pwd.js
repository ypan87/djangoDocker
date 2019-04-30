let form = document.getElementById("forgetPwdForm");
let message = document.getElementsByClassName("success")[0];
let email = document.getElementById("email");
let emailError = document.getElementById("emailError");
let captcha = document.getElementById("id_captcha_1");
let captchaError = document.getElementById("captchaError");
let forgetPwdBtn = document.getElementsByClassName("forget-pwd-submit-button")[0];
let emailRegExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

captcha.placeholder = "输入4位验证码";

// 初次点击再离开输入框之后进行value值检查
function inputBlurEvent() {
    if (this.value == "") {
        let error = this.parentElement.nextElementSibling;
        error.className = "forget-pwd-require-error";
        if (this.id == "email") {
            error.innerHTML="请输入邮箱";
        } else if (this.id == "id_captcha_1") {
            error.innerHTML = "请输入验证码";
        }
    }
}

// 点击输入框进行输入时进行检查
function inputFocusEvent() {
    let error = this.parentElement.nextElementSibling;
    if (!error.classList.contains("hidden")) {
        error.innerHTML = "";
        error.classList.add("hidden");
    }
}

// 点击错误提醒时
function errorClickEvent() {
    this.innerHTML="";
    this.classList.add("hidden");
    let input = this.previousElementSibling.firstElementChild;
    if (this.id = "captchaError") {}
    input = this.previousElementSibling.lastElementChild;
    input.focus();
}

function formSubmit() {
    event.preventDefault();
    let isRight = formValidate();
    if (!isRight) {
        return false;
    }

    valueSubmit();
}

// 前端数据验证
// require验证由input required检查
function formValidate() {
    let isRight = true;
    let emailErrors = [];

    // email 正则表达式检查
    let emailTest = emailRegExp.test(email.value);
    if (!emailTest) {
        emailErrors.push("请输入正确的邮箱格式");
        if (isRight == true) {
            isRight = false;
        }
    }

    // 检查之后动作
    if (emailErrors.length > 0) {
        emailError.className = "forget-pwd-common-error";
        emailError.innerHTML=emailErrors[0];
    }

    return isRight;
}

function valueSubmit() {
    $.ajax({
        cache: false,
        type: "post",
        dataType:'json',
        url:"/forget/",
        data: $('#forgetPwdForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){},
        success: function(data){
            if (data.status == "ok") {
                message.classList.remove("hidden");
                message.innerHTML = "邮件发送成功，请前往邮箱点击重置密码链接";
            }
        },

        complete: function(XMLHttpRequest){}
    })
}

function btnClick() {
    message.classList.add("hidden");
    message.innerHTML = "";
}

email.addEventListener("blur", inputBlurEvent);
email.addEventListener("focus", inputFocusEvent);
captcha.addEventListener("blur", inputBlurEvent);
captcha.addEventListener("focus", inputFocusEvent);

emailError.addEventListener("click", errorClickEvent);
captchaError.addEventListener("click", errorClickEvent);

form.addEventListener("submit", formSubmit);
forgetPwdBtn.addEventListener("click", btnClick);