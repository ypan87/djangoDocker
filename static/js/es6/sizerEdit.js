/**
 * Created by yifan_pan on 2019/10/15.
 */
import {language, errorCode, unit, Validation, toastrTime} from "./base"
import * as WorkingCondition from "../sizer_create/models/WorkingCondition";
import * as workingConditionView from "../sizer_create/views/workingConditionView";
import * as cardView from "../sizer_create/views/cardView";
import * as sizerEditView from "../sizer_edit/views/sizerEditView";
import {
    getLang, renderLoading, removeLoading, unitSelectValue,
    disableBtn, ableBtn, Request, handleResponse
} from "../util/util";

// add the validation rule
let validator = new Validation();
let lang = getLang();
let conditions = new WorkingCondition.Conditions();
let conditionTables = new workingConditionView.conditionTables();

const validationInit = function(validator) {
    validator.add(sizerEditView.DOMs.form.projectAltitude, [{
        strategy: 'isNumber',
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.projectInletPres, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.projectUnitsNum, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.projectSafetyFactor, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.projectEnvTemp, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.ratingFlow, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        },
        {
            strategy: "minValue:0",
            errorMsg: {
                "cn": "请填写大于0的数字",
                "en": "Please Input Number Larger Than 0"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPressure, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerEditView.DOMs.form.ratingTemp, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingHumi, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        },
        {
            strategy: "minValue:0",
            errorMsg: {
                "cn": "请填写大于0的数字",
                "en": "Please Input Number Larger Than 0"
            },
        },
        {
            strategy: "maxValue:100",
            errorMsg: {
                "cn": "请填写小于100的数字",
                "en": "Please Input Number Smaller Than 100"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointInletPressure, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointInletTemp, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointHumi, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        },
        {
            strategy: "minValue:0",
            errorMsg: {
                "cn": "请填写大于0的数字",
                "en": "Please Input Number Larger Than 0"
            },
        },
        {
            strategy: "maxValue:100",
            errorMsg: {
                "cn": "请填写小于100的数字",
                "en": "Please Input Number Smaller Than 100"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointInletLoss, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointOutletLoss, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.ratingPointOutPressure, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.maxFlowCoeff, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerEditView.DOMs.form.maxPressureCoeff, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);
};
validationInit(validator);

const displayError = function(errorMsg) {
    let inputError = this.parentElement.getElementsByClassName('input-error')[0];
    if (!inputError) return;
    inputError.innerHTML = errorMsg[lang];
    if (inputError.classList.contains('hidden')) {
        inputError.classList.remove('hidden');
    }
};

const validateFields = function() {
    let results = validator.start();
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

// add event listener
sizerEditView.DOMs.form.addEventListener("click", function(event) {
    if(event.target.matches('.card-header, .card-header *')) {
        let cardHeader = event.target.closest('.card-header');
        cardView.fold(cardHeader);
    }
});

sizerEditView.DOMs.conditionSec.addEventListener('click', function(event) {
    if (event.target.matches('.condition-table-close, .condition-table-close *')) {
        ctrlDeleteWorkingCondition(event);
    } else if (event.target.matches('.row-add, .row-add * ')) {
        ctrlAddWorkingPoint(event);
    } else if (event.target.matches('.row-del, .row-del *')) {
        ctrlDeleteWorkingPoint(event);
    } else if (event.target.matches('.condition-table-add')) {
        // 停止冒泡
        event.stopPropagation();
        ctrlAddWorkingCondition();
    }
});

sizerEditView.DOMs.form.addEventListener('keyup', function(event) {
    if (event.target.matches('.value-input input')) {
        sizerEditView.clearFormInputError(event.target);
    }
});

sizerEditView.DOMs.unitSelect.addEventListener("change", function(event) {
    renderLoading(sizerEditView.DOMs.loadIcon);
    setupUnits();
    removeLoading(sizerEditView.DOMs.loadIcon);
});

sizerEditView.DOMs.uploadBtn.addEventListener("click", function(event) {
    sizerEditView.DOMs.uploadFile.click();
});

sizerEditView.DOMs.uploadFile.addEventListener("change", function(event) {
    let fileName = this.files[0].name;
    let translation = {
        "cn": "文件名：",
        "en": "Filename: "
    };
    sizerEditView.DOMs.uploadLb.innerHTML = translation[lang] + fileName;
});

sizerEditView.DOMs.checkBtn.addEventListener('click', function(event) {
    // 删除图表区域
    sizerEditView.deleteGraphSec();
    // disable提交按钮
    disableBtn(sizerEditView.DOMs.checkBtn);
    // loading图标
    renderLoading(sizerEditView.DOMs.loadIcon);
    if (!formValidation()) {
        return false;
    }
    // 获取最终传输数据
    sizerEditView.DOMs.wkConditionInput.value = JSON.stringify(workingConditionView.getConditionTablesData());

    sendCheckRequest();

});

const formValidation = function() {
    if (!validateFields()) {
        removeLoading(sizerEditView.DOMs.loadIcon);
        ableBtn(sizerEditView.DOMs.checkBtn);
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

const sendCheckRequest = async function() {
    let formData = new FormData(document.querySelector(`#${sizerEditView.DOMstrings.turboForm}`));
    let checkRequest = new Request(sizerEditView.URLs.checkBlower, formData);

    try {
        await checkRequest.getResults();
        removeLoading(sizerEditView.DOMs.loadIcon);
        ableBtn(sizerEditView.DOMs.checkBtn);
        let result = checkRequest.data;
        if (result.status == "failure") {
            toastr.options = {
                timeOut: toastrTime["danger"],
                positionClass: 'toast-top-right'
            };
            toastr.error(errorCode[lang][result.errorCode]);
            return false;
        }

        sizerEditView.generateGraph(result);
        let form = document.getElementById(sizerEditView.DOMstrings.excelForm);
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            form.querySelector(`[name=${sizerEditView.DOMstrings.excelField}]`).value = JSON.stringify(result);
            form.submit();
        });

        let saveBtn = document.getElementById(sizerEditView.DOMstrings.saveBtn);
        saveBtn.addEventListener("click", function(event) {
            renderLoading(sizerEditView.DOMs.loadIcon);
            disableBtn(saveBtn);
            sendSaveRequest(formData, saveBtn);
        });

    } catch (err) {
        removeLoading(sizerEditView.DOMs.loadIcon);
        ableBtn(sizerEditView.DOMs.checkBtn);
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["NetworkError"]
        );
    }
};

const sendSaveRequest = async function(formData, btn) {
    let saveRequest = new Request(sizerEditView.URLs.saveSizer, formData);
    try {
        await saveRequest.getResults();
        removeLoading(sizerEditView.DOMs.loadIcon);
        handleResponse(saveRequest.data, "updateSizerSuccess", lang);
    } catch (err) {
        removeLoading(sizerEditView.DOMs.loadIcon);
        ableBtn(btn);
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["NetworkError"]
        );
    }
};

const ctrlAddWorkingCondition = function(option) {
    let newWorkingOption = conditions.addWkCond(option);
    conditionTables.addWkTable(newWorkingOption, validator);
};

const ctrlDeleteWorkingCondition = function(event) {
    let table = event.target.closest('.col-sm-4');
    let cond_length = conditions.getWkCondInUse();
    if (cond_length <= 1) {
        toastr.options = {
            timeOut: toastrTime[lang]["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["wkConditionDeleteError"]
        );
        return false;
    }
    conditionTables.deleteWkTable(table, validator);
    let id = parseInt(table.dataset.tableid);
    conditions.deleteWkCond(id);
};

const ctrlAddWorkingPoint = function(event) {
    let addRow = event.target.closest('tr');
    let input = workingConditionView.getRowInput(addRow);
    workingConditionView.addWkPoint(input, addRow, validator);
    workingConditionView.clearRowInput(addRow);
};

const ctrlDeleteWorkingPoint = function(event) {
    let pointLength = event.target.closest('table').querySelectorAll(".point").length;
    if (pointLength <= 1) {
        toastr.options = {
            timeOut: toastrTime[lang]["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang]["wkPointDeleteError"]
        );
        return;
    }
    let row = event.target.closest('tr');
    workingConditionView.deleteWkPoint(row, validator);
};

const initTables = function() {
    var tables_num = document.querySelectorAll(".condition-sec table").length;

    conditions.initWkConds(tables_num);
};

const setupUnits = function() {
    let unitSelection = unitSelectValue(sizerEditView.DOMs.unitSelect);
    let allUnits = document.querySelectorAll(`[${sizerEditView.DOMstrings.unitAttribute}]`);
    for (let i =0; i < allUnits.length; i++) {
        let unitValue = allUnits[i].dataset[sizerEditView.DOMstrings.dataAttribute];
        allUnits[i].innerHTML = "(" + unit[unitSelection][unitValue] + ")";
    }
};

setupUnits();
initTables();