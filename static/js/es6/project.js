/**
 * Created by yifan_pan on 2019/10/15.
 */
import {errorCode, Validation, toastrTime} from "./base";
import {DOMs, DOMstrings, URLs} from "../project/views/projectView";
import {
    Request, getLang, ableCreateBtn, disableCreateBtn,
    clearFormInputError, removeLoading, renderLoading,
    handleResponse
} from "../util/util";

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
        ableCreateBtn(DOMs.createBtn);
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
DOMs.form.addEventListener("keyup", function(event) {
    if (event.target.matches('.value-input input')) {
        clearFormInputError(event.target);
    }
});

DOMs.table.addEventListener("click", function(event) {
    deleteSizer(event.target);
});

DOMs.form.addEventListener("submit", function() {
    event.preventDefault();
    disableCreateBtn(DOMs.createBtn);
    renderLoading(DOMs.loadIcon);
    if (!formValidation()) {
        return false;
    }

    sendCreateRequest();
});

const deleteSizer = function(target) {
    if (!target.matches(".delete")) return false;

    showDeleteTipModal();

    let url = target.dataset.url;

    DOMs.confirmDeleteBtn.addEventListener("click", function(event) {
        sendDeleteRequest(url);
    })
};

// send create project request
const sendCreateRequest = async function() {
    let formData = $(`#${DOMstrings.form}`).serialize();
    let request = new Request(URLs.editProject, formData);

    try {
        await request.getResults();
        removeLoading(DOMs.loadIcon);
        ableCreateBtn(DOMs.createBtn);
        handleResponse(request.data, "editProjectSuccess", lang);
    } catch (err) {
        removeLoading(DOMs.loadIcon);
        ableCreateBtn(DOMs.createBtn);
        toastr.options = {
            timeOut: toastrTime.toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode.errorCode[lang]["NetworkError"]
        );
    }
};

// send delete sizer request
const sendDeleteRequest = async function(url) {
    hideDeleteTipModal();
    let request = new Request(url, "");

    try {
        await request.getResults();
        handleResponse(request.data, "deleteSizerSuccess", lang);
    } catch (err) {
        toastr.options = {
            timeOut: toastrTime.toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode.errorCode[lang]["NetworkError"]
        );
    }
};

const showDeleteTipModal = function() {
    $(`#${DOMstrings.deleteModal}`).modal('show');
};

const hideDeleteTipModal = function() {
    $(`#${DOMstrings.deleteModal}`).modal('hide');
};

const setupTables = function() {
    $(document).ready(function() {
        $('#sizerTable').DataTable();
    } );
};

// setup the initial table
setupTables();