let email = document.getElementById("email");
let password = document.getElementById("password");
let captcha = document.getElementById("id_captcha_1");
let emailError = document.getElementById("emailError");
let passwordError = document.getElementById("passwordError");
let captchaError = document.getElementById("captchaError");
let form = document.getElementById("registerForm");
let emailRegExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
let passwordRegExp = /^[a-zA-Z0-9_-]{6,20}$/;
let switchBth = document.getElementById("switchBtn");

captcha.placeholder = "输入4位验证码";

$('.captcha').click(function () {
    $.getJSON("/captcha/refresh/", function (result) {
        $('.captcha').attr('src', result['image_url']);
        $('#id_captcha_0').val(result['key'])
    });
});

switchBth.onclick = function () {
    location.href = "/login";
};

// 初次点击再离开输入框之后进行value值检查
function inputBlurEvent() {
    if (this.value == "") {
        let error = this.parentElement.nextElementSibling;
        error.className = "register-login-require-error";
        if (this.id == "email") {
            error.innerHTML="请输入邮箱";
        } else if (this.id == "password") {
            error.innerHTML="请输入密码";
        } else if (this.id == "id_captcha_1") {
            error.innerHTML="请输入验证码";
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

// form表单进行提交后的动作
// 分为两种错误进行显示
// 一种是require显示在input中显示
// 另一种是其他错误，在input后面显示
function formSubmit(event) {
    let isRight = formValidate();
    event.preventDefault();
    if (!isRight) {
        return false;
    }

    valueSubmit();

}


function valueSubmit() {
    $.ajax({
        cache: false,
        type: "post",
        dataType:'json',
        url:"/register/",
        data: $('#registerForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){},
        success: function(data){
            if (data.status == "ok") {
                window.location.href = "/login";
                return false;
            }

            for (let key in data) {
                if (key == "email") {
                    emailError.className = "register-login-common-error";
                    emailError.innerHTML = data[key];
                } else if (key == "password") {
                    passwordError.className = "register-login-common-error";
                    passwordError.innerHTML = data[key];
                } else if (key == "captcha") {
                    captchaError.className = "register-login-captcha-error";
                    captchaError.innerHTML = data[key];
                }
            }
        },

        complete: function(XMLHttpRequest){}
    });
}

// 前端数据验证
// require验证由input required检查
function formValidate() {
    let isRight = true;
    let emailErrors = [];
    let passwordErrors = [];

    // email 正则表达式检查
    let emailTest = emailRegExp.test(email.value);
    if (!emailTest) {
        emailErrors.push("请输入正确的邮箱格式");
        if (isRight == true) {
            isRight = false;
        }
    }

    // password长度检查
    let passwordValue = password.value;
    if (passwordValue.length < 6) {
        passwordErrors.push("密码长度不足");
        if (isRight == true) {
            isRight = false;
        }
    } else if (passwordValue.length > 20) {
        passwordErrors.push("密码长度过长");
        if (isRight == true) {
            isRight = false;
        }
    }

    // password 正则表达式检查
    let passwordTest = passwordRegExp.test(passwordValue);
    if (!passwordTest) {
        passwordErrors.push("密码格式错误");
        if (isRight == true) {
            isRight = false;
        }
    }

    // 检查之后动作
    if (emailErrors.length > 0) {
        emailError.className = "register-login-common-error";
        emailError.innerHTML=emailErrors[0];
    }
    if (passwordErrors.length > 0) {
        passwordError.className = "register-login-common-error";
        passwordError.innerHTML=passwordErrors[0];
    }
    return isRight;
}

email.addEventListener("blur", inputBlurEvent);
email.addEventListener("focus", inputFocusEvent);

password.addEventListener("blur", inputBlurEvent);
password.addEventListener("focus", inputFocusEvent);

captcha.addEventListener("blur", inputBlurEvent);
captcha.addEventListener("focus", inputFocusEvent);

emailError.addEventListener("click", errorClickEvent);
passwordError.addEventListener("click", errorClickEvent);
captchaError.addEventListener("click", errorClickEvent);
// 处理表单提交
form.addEventListener("submit", formSubmit)