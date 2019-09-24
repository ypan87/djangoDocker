var baseView = (function() {
    var DOMs = {
        form: document.querySelector('#projectForm'),
        loadIcon: document.querySelector('.wrapper'),
        createBtn: document.querySelector('button')
    };

    var DOMStrings = {
        form: "projectForm"
    };

    var URLs = {
        createProject: window.location.pathname,
    };

    return {
        getDOMs: function() {
            return DOMs;
        },
        getDOMStrings: function() {
            return DOMStrings;
        },
        getURLs: function() {
            return URLs;
        },
        renderLoading: function() {
            if (DOMs.loadIcon.classList.contains('hidden')) {
                DOMs.loadIcon.classList.remove('hidden');
            }
        },
        removeLoading: function() {
            if (!DOMs.loadIcon.classList.contains('hidden')) {
                DOMs.loadIcon.classList.add('hidden');
            }
        },
        disableCreateBtn: function() {
            DOMs.createBtn.disabled = true;
        },
        ableCreateBtn: function() {
            DOMs.createBtn.disabled = false;
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

    var form = baseView.getDOMs().form;

    var validator = new Validator();

    validator.add(form.projectName, [{
        strategy: 'isNonEmpty',
        errorMsg: '输入值不能为空',
    }]);

    validator.add(form.projectAddress, [{
        strategy: "isNonEmpty",
        errorMsg: '输入值不能为空',
    }]);

    validator.add(form.projectIndex, [{
        strategy: 'isNonEmpty',
        errorMsg: '输入值不能为空',
    }]);

    validator.add(form.projectEngineer, [{
        strategy: "isNonEmpty",
        errorMsg: '输入值不能为空',
    }]);

    var displayError = function(errorMsg) {
        let inputError = this.parentElement.getElementsByClassName('input-error')[0];
        if (!inputError) return;
        inputError.innerHTML = errorMsg;
        if (inputError.classList.contains('hidden')) {
            inputError.classList.remove('hidden');
        }
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

    var setupEventListeners = function() {
        var DOMs = baseView.getDOMs();
        var DOMStrings = baseView.getDOMStrings();
        var URLs = baseView.getURLs();
        DOMs.form.addEventListener("submit", function(event) {
            event.preventDefault();
            baseView.disableCreateBtn();
            baseView.renderLoading();
            if (!formValidation()) {
                baseView.removeLoading();
                baseView.ableCreateBtn();
                toastr.options = {
                    timeOut: 200,
                    positionClass: 'toast-top-right'
                };
                toastr.error("参数错误，请修改后提交");
                return false;
            }
            var formData = $(`#${DOMStrings.form}`).serialize();
            var requester = baseCtrl.createRequester(URLs.createProject, formData);
            var promise = requester.ajaxRequest();
            promise.then(function(result) {
                baseView.removeLoading();
                baseView.ableCreateBtn();
                if (result.status == "success") {
                    toastr.options = {
                        timeOut: 200,
                        positionClass: 'toast-top-right',
                        onHidden: function() {window.location.href=result.url}
                    };
                    toastr.success("创建成功");
                } else if (result.status == "failure") {
                    toastr.options = {
                        timeOut: 200,
                        positionClass: 'toast-top-right'
                    };
                    toastr.error(result.errorCode);
                }
            })
        })
    };

    var formValidation = function() {
        return vldCtrl.validateFields();
    };

    return {
        init: function() {
            setupEventListeners();
        },
    }
})(baseView, baseController, validateCtrl);

controller.init();

