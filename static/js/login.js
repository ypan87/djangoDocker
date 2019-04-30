let email = document.getElementById("email");
let password = document.getElementById("password");
let emailError = document.getElementById("emailError");
let passwordError = document.getElementById("passwordError");
let loginBtn = document.getElementById("loginBtn");
let passwordRegExp = /^[a-zA-Z0-9_-]{6,20}$/;
let switchBth = document.getElementById("switchBtn");
let forgetPwdBth = document.getElementsByClassName("login-forget-password-btn")[0];

// 点击跳转到注册页面
switchBth.onclick = function () {
    location.href = "/register";
};

forgetPwdBth.onclick = function () {
    window.open("/forget", "_blank");
};

// 初次点击再离开输入框之后进行value值检查
function inputBlurEvent() {
    if (this.value == "") {
        let error = this.parentElement.nextElementSibling;
        error.className = "register-login-require-error";
        if (this.id == "email") {
            error.innerHTML = "请输入邮箱";
        } else if (this.id == "password") {
            error.innerHTML = "请输入密码"
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
    input.focus();
}

// form表单进行提交后的动作
// 分为两种错误进行显示
// 一种是require显示在input中显示
// 另一种是其他错误，在input后面显示
function formSubmit(event) {
    event.preventDefault();
    let isRight = formValidate();
    if (!isRight) {
        return false;
    }
    valueSubmit();
    return false;
}

// ajax提交表达
// 以及数据处理
function valueSubmit() {
    $.ajax({
        cache: false,
        type: "post",
        dataType:'json',
        url:"/login/",
        data: $('#loginForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){},
        success: function(data){
            if (data.status == "ok") {
                window.location.href = "/";
                return false;
            }

            for (let key in data) {
                if (key == "email") {
                    emailError.className = "register-login-common-error";
                    emailError.innerHTML = data[key];
                } else if (key == "password") {
                    passwordError.className = "register-login-common-error";
                    passwordError.innerHTML = data[key];
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
    let passwordErrors = [];

    // 密码长度检差
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

emailError.addEventListener("click", errorClickEvent);
passwordError.addEventListener("click", errorClickEvent);

// 处理表单提交
loginBtn.addEventListener("click", formSubmit);
