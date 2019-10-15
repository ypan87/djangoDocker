/**
 * Created by yifan_pan on 2019/10/14.
 */
import {Request, getLang} from "../util/util";
import {errorCode, language, toastrTime, unit, Validation} from "./base";
import * as projectCreate from "../project_create/views/projectCreateView";

// add the validation rule
let validator = new Validation();
let lang = getLang();

validator.add(projectCreate.DOMs.form.projectName, [{
    strategy: 'isNonEmpty',
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(projectCreate.DOMs.form.projectAddress, [{
    strategy: "isNonEmpty",
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(projectCreate.DOMs.form.projectIndex, [{
    strategy: 'isNonEmpty',
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(projectCreate.DOMs.form.projectEngineer, [{
    strategy: "isNonEmpty",
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

const displayError = function(errorMsg) {
    let inputError = this.parentElement.getElementsByClassName('input-error')[0];
    if (!inputError) return;
    inputError.innerHTML = errorMsg[lang];
    if (inputError.classList.contains('hidden')) {
        inputError.classList.remove('hidden');
    }
};

const validateFields = function() {
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
};

// clear error shown in input
const clearFormInputError = function(event) {
    projectCreate.clearFormInputError(event.target);
};

const formValidation = function() {
    if (!validateFields()) {
        projectCreate.removeLoading();
        projectCreate.ableCreateBtn();
        toastr.options = {
            timeOut: toastrTime.toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode.errorCode[lang]["ParameterError"]
        );
        return false;
    }
    return true;
};

// add event listener
projectCreate.DOMs.form.addEventListener("keyup", function(event) {
    if (event.target.matches('.value-input input')) {
        clearFormInputError(event);
    }
});

projectCreate.DOMs.form.addEventListener("submit", function(event) {
    event.preventDefault();
    projectCreate.disableCreateBtn();
    projectCreate.renderLoading();
    if (!formValidation()) {
        return false;
    }

    sendCreateRequest();

});

// send create project request
const sendCreateRequest = async function() {
    let formData = $(`#${projectCreate.DOMstrings.form}`).serialize();
    let request = new Request(projectCreate.URLs.createProject, formData);

    try {
        await request.getResults();
        projectCreate.removeLoading();
        projectCreate.ableCreateBtn();
        let result = request.data;
        if (result.status == "success") {
            toastr.options = {
                timeOut: toastrTime.toastrTime["success"],
                positionClass: 'toast-top-right',
                onHidden: function() {window.location.href=result.url}
            };
            toastr.success(
                errorCode.errorCode[lang]["createProjectSuccess"]
            );
        } else if (result.status == "failure") {
            toastr.options = {
                timeOut: toastrTime.toastrTime["danger"],
                positionClass: 'toast-top-right'
            };
            toastr.error(
                errorCode.errorCode[lang][result.errorCode]
            );
        }
    } catch (err) {
        projectCreate.removeLoading();
        projectCreate.ableCreateBtn();
        toastr.options = {
            timeOut: toastrTime.toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode.errorCode[lang]["NetworkError"]
        );
    }
};
