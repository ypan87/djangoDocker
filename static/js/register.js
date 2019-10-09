var baseView = (function() {
    var DOMs = {
        email: document.getElementById("email"),
        password: document.getElementById("password"),
        captcha: document.getElementById("id_captcha_1"),
        registerForm: document.getElementById("registerForm"),
        switchBtn: document.getElementById("switchBtn"),
        emailError: document.getElementById("emailError"),
        passwordError: document.getElementById("passwordError"),
        captchaError: document.getElementById("captchaError"),
        registerBtn: document.getElementById("registerBtn"),
    };

    var URLs = {
        register: "/register/",
        login: "/login/"
    };

    var DOMStrings = {
        registerForm: "registerForm"
    };

    return {
        getDOMs: function() {
            return DOMs;
        },
        getURLs: function() {
            return URLs;
        },
        getDOMStrings: function() {
            return DOMStrings;
        }
    }
})();

var baseController = (function() {
    var getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    var Requester = function(url, data) {
        this.data = data;
        this.url = url;
    };

    Requester.prototype.ajaxRequest = function() {
        var self = this;

        return new Promise(function(resolve, reject) {
            $.ajax({
                cache: false,
                type: 'POST',
                url: self.url,
                headers:{ "X-CSRFtoken": getCookie('csrftoken')},
                data: self.data,
                async: true,
                beforeSend:function (xhr,settings) {
                },
                success: function(data) {
                    resolve(data);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                }
            });
        });
    };

    return {
        createRequester: function(url, data) {
            return new Requester(url, data);
        },

    }
})();

var validateCtrl = (function(baseView) {

    var form = baseView.getDOMs().registerForm;
    var validator = new Validator();

    validator.add(form.email, [
        {
            strategy: 'isNonEmpty',
            errorMsg: "Input Value Required",
        },
        {
            strategy: "email",
            errorMsg: "Email Format Wrong",
        },
    ]);

    validator.add(form.password, [
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

    var displayError = function(errorMsg) {
        let inputError = this.parentElement.nextElementSibling;
        if (!inputError) return;
        inputError.className = "register-login-common-error";
        inputError.innerHTML = errorMsg;
    };

    return {
        validateFields: function() {
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
        },
    }
})(baseView);

var controller = (function(baseView, baseCtrl, vldCtrl) {
    // TODO 页面点击有问题
    var DOMs = baseView.getDOMs();
    var URLs = baseView.getURLs();
    var DOMStrings = baseView.getDOMStrings();

    var setupEventListeners = function() {
        DOMs.switchBtn.addEventListener("click", function(event) {
            window.location.href = URLs.login;
        });

        DOMs.registerForm.addEventListener("blur", function(event) {
            if (!event.target.matches("input")) {return false;}
            if (event.target.value == "") {
                var error = event.target.parentElement.nextElementSibling;
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
            var error = event.target.parentElement.nextElementSibling;
            if (!error.classList.contains("hidden")) {
                error.innerHTML = "";
                error.classList.add("hidden");
            }
        }, true);

        DOMs.registerBtn.addEventListener("click", function(event) {
            if (!vldCtrl.validateFields()) {
                toastr.options = {
                    timeOut: toastr_time["danger"],
                    positionClass: 'toast-top-right'
                };
                toastr.error(
                    "Parameters Wrong, Please Correct"
                );
                return false;
            }
            var formData = $(`#${DOMStrings.registerForm}`).serialize();
            var url = URLs.register;
            var requester = baseCtrl.createRequester(url, formData);
            var promise = requester.ajaxRequest();
            promise.then(function(result) {
                if (result.status == "success") {
                    toastr.options = {
                        timeOut: toastr_time["success"],
                        positionClass: 'toast-top-right',
                        onHidden: function() {window.location.href=result.url}
                    };
                    toastr.success(
                        errorCode["en"]["registerSuccess"]
                    );
                    return false;
                } else if (result.status == "failure") {
                    toastr.options = {
                        timeOut: toastr_time["danger"],
                        positionClass: 'toast-top-right'
                    };
                    toastr.error(
                        errorCode["en"][result.errorCode]
                    );
                }
            })
        });

        DOMs.emailError.addEventListener("click", errorClickEvent);
        DOMs.passwordError.addEventListener("click", errorClickEvent);
        DOMs.captchaError.addEventListener("click", errorClickEvent);
    };

    var setupCaptcha = function() {
        DOMs.captcha.placeholder = "Captcha";

        $('.captcha').click(function () {
            $.getJSON("/captcha/refresh/", function (result) {
                $('.captcha').attr('src', result['image_url']);
                $('#id_captcha_0').val(result['key'])
            });
        });
    };

    function errorClickEvent() {
        this.innerHTML="";
        this.classList.add("hidden");
        let input = this.previousElementSibling.firstElementChild;
        if (this.id == "captchaError") {
            input = this.previousElementSibling.lastElementChild;
        }
        input.focus();
    }

    return {
        init: function() {
            setupEventListeners();
            setupCaptcha();
        }
    }
})(baseView, baseController, validateCtrl);

controller.init();