/**
 * Created by yifan_pan on 2019/10/14.
 */
import {
    Request, getLang, ableBtn, disableBtn,
    clearFormInputError, removeLoading, renderLoading,
    handleResponse
} from "../util/util";
import {errorCode, toastrTime, Validation} from "./base";
import {DOMs, DOMstrings, URLs} from "../project_create/views/projectCreateView";

// add the validation rule
let validator = new Validation();
let lang = getLang();

validator.add(DOMs.form.projectName, [{
    strategy: 'isNonEmpty',
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(DOMs.form.projectAddress, [{
    strategy: "isNonEmpty",
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(DOMs.form.projectIndex, [{
    strategy: 'isNonEmpty',
    errorMsg: {
        "cn": "输入值不能为空",
        "en": "Input value cannot be empty"
    },
}]);

validator.add(DOMs.form.projectEngineer, [{
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

const formValidation = function() {
    if (!validateFields()) {
        removeLoading(DOMs.loadIcon);
        ableBtn(DOMs.createBtn);
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["ParameterError"]
        );
        return false;
    }
    return true;
};

// add event listener
DOMs.form.addEventListener("keyup", function(event) {
    if (event.target.matches('.value-input input')) {
        clearFormInputError(event.target);
    }
});

DOMs.form.addEventListener("submit", function(event) {
    event.preventDefault();
    disableBtn(DOMs.createBtn);
    renderLoading(DOMs.loadIcon);
    if (!formValidation()) {
        return false;
    }

    sendCreateRequest();

});

// send create project request
const sendCreateRequest = async function() {
    let formData = $(`#${DOMstrings.form}`).serialize();
    let request = new Request(URLs.createProject, formData);

    try {
        await request.getResults();
        removeLoading(DOMs.loadIcon);
        ableBtn(DOMs.createBtn);
        handleResponse(request.data, "createProjectSuccess", lang);
    } catch (err) {
        removeLoading(DOMs.loadIcon);
        ableBtn(DOMs.createBtn);
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["NetworkError"]
        );
    }
};
