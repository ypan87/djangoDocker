let form = document.getElementById("pwdResetForm");
let firstError = document.getElementById("password1Error");
let secondError = document.getElementById("password2Error");
let password1 = document.getElementById("password1");
let password2 = document.getElementById("password2");
let passwordRegExp = /^[a-zA-Z0-9_-]{6,20}$/;

// 初次点击再离开输入框之后进行value值检查
function inputBlurEvent() {
    if (this.value == "") {
        let error = this.parentElement.nextElementSibling;
        error.className = "forget-pwd-require-error";
        if (this.id == "password1") {
            error.innerHTML="请输入密码";
        } else if (this.id == "password2") {
            error.innerHTML="请输入密码";
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
    let password1Errors = [];

    // password长度检查
    let password1Value = password1.value;
    if (password1Value.length < 6) {
        password1Errors.push("密码长度不足");
        if (isRight == true) {
            isRight = false;
        }
    } else if (password1Value.length > 20) {
        password1Errors.push("密码长度过长");
        if (isRight == true) {
            isRight = false;
        }
    }

    // password 正则表达式检查
    let password1Test = passwordRegExp.test(password1Value);
    if (!password1Test) {
        password1Errors.push("密码格式错误");
        if (isRight == true) {
            isRight = false;
        }
    }

    // 检查之后动作
    if (password1Errors.length > 0) {
        firstError.className = "forget-pwd-common-error";
        firstError.innerHTML = password1Errors[0];
    }
    return isRight;
}

function valueSubmit() {
    $.ajax({
        cache: false,
        type: "post",
        dataType:'json',
        url:"/modify_pwd/",
        data: $('#pwdResetForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){},
        success: function(data){
            if (data.status == "ok") {
                window.location.href = "/login";
                return false;
            }
            for (let key in data) {
                if (key == "user") {
                    window.location.href = "/forget"
                } else if (key == "password1") {
                    firstError.className = "forget-pwd-common-error";
                    firstError.innerHTML = data[key];
                } else if (key == "password2") {
                    secondError.className = "forget-pwd-common-error";
                    secondError.innerHTML = data[key];
                }

            }
        },

        complete: function(XMLHttpRequest){}
    })
}

password1.addEventListener("blur", inputBlurEvent);
password1.addEventListener("focus", inputFocusEvent);

password2.addEventListener("blur", inputBlurEvent);
password2.addEventListener("focus", inputFocusEvent);

firstError.addEventListener("click", errorClickEvent);
secondError.addEventListener("click", errorClickEvent);

form.addEventListener("submit", formSubmit);