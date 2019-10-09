var baseView = (function() {
    var DOMs = {
        emailError: document.getElementById("emailError"),
        captchaError: document.getElementById("captchaError"),
        forgetPwdForm: document.getElementById("forgetPwdForm"),
        email: document.getElementById("email"),
        captcha: document.getElementById("id_captcha_1"),
        forgetPwdBtn: document.getElementsByClassName("forget-pwd-submit-button")[0],
    };

    var URLs = {
        forgetPwd: "/forget/"
    };

    var DOMStrings = {
        forgetPwdForm: "forgetPwdForm"
    };

    return {
        getDOMs: function() {
            return DOMs;
        },
        getDOMStrings: function() {
            return DOMStrings;
        },
        getLang: function() {
            return window.location.pathname.split('/')[1];
        },
        getURLs: function() {
            return URLs;
        },
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
    var lang = baseView.getLang();
    var form = baseView.getDOMs().forgetPwdForm;
    var validator = new Validator();

    validator.add(form.email, [
        {
            strategy: 'isNonEmpty',
            errorMsg: {
                "en": "Input Value Required",
                "cn": "输入值不能为空"
            },
        },
        {
            strategy: "email",
            errorMsg: {
                "en": "Email Format Incorrect",
                "cn": "邮箱格式错误"
            }
        }

    ]);

    var displayError = function(errorMsg) {
        let inputError = this.parentElement.nextElementSibling;
        if (!inputError) return;
        inputError.className = "forget-pwd-common-error";
        inputError.innerHTML = errorMsg[lang];
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

    var DOMs = baseView.getDOMs();
    var DOMStrings = baseView.getDOMStrings();
    var lang = baseView.getLang();
    var URLs = baseView.getURLs();
    var setupEventListeners = function() {
        DOMs.forgetPwdBtn.addEventListener("click", function(event) {
            if (!vldCtrl.validateFields()) {
                toastr.options = {
                    timeOut: 200,
                    positionClass: 'toast-top-right'
                };
                toastr.error(
                    "Parameters Wrong, Please Correct"
                );
                return false;
            }
            var formData = $(`#${DOMStrings.forgetPwdForm}`).serialize();
            var url = "/" + lang + URLs.forgetPwd;
            var requester = baseCtrl.createRequester(url, formData);
            var promise = requester.ajaxRequest();
            promise.then(function(result) {
                if (result.status == "success") {
                    toastr.options = {
                        timeOut: 200,
                        positionClass: 'toast-top-right',
                        onHidden: function() {window.location.href=result.url}
                    };
                    toastr.success(
                        errorCode[lang]["findPwdSuccess"]
                    );
                    return false;
                } else if (result.status == "failure") {
                    toastr.options = {
                        timeOut: 200,
                        positionClass: 'toast-top-right'
                    };
                    toastr.error(
                        errorCode[lang][result.errorCode]
                    );
                }
            })
        });

        DOMs.forgetPwdForm.addEventListener("blur", function(event) {
            if (!event.target.matches("input")) {return false;}
            if (event.target.value == "") {
                var error = event.target.parentElement.nextElementSibling;
                error.className = "forget-pwd-require-error";
                if (event.target.id == "email") {
                    error.innerHTML = language[lang]["emailNonEmpty"];
                } else if (event.target.id == "id_captcha_1") {
                    error.innerHTML = language[lang]["captchaNonEmpty"];
                }
            }
        }, true);

        DOMs.forgetPwdForm.addEventListener("focus", function(event) {
            if (!event.target.matches("input")) {return false;}
            var error = event.target.parentElement.nextElementSibling;
            if (!error.classList.contains("hidden")) {
                error.innerHTML = "";
                error.classList.add("hidden");
            }
        }, true);

        DOMs.emailError.addEventListener("click", errorClickEvent);
        DOMs.captchaError.addEventListener("click", errorClickEvent);
    };

    var setupCaptcha = function() {
        DOMs.captcha.placeholder = language[lang]["captcha"];

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

