/**
 * Created by yifan_pan on 2019/10/15.
 */
import {errorCode, language, toastrTime, unit, Validation} from "./base";
import * as WorkingCondition from "../sizer_create/models/WorkingCondition";
import * as cardView from "../sizer_create/views/cardView";
import * as sizerCreateView from "../sizer_create/views/sizerCreateView";
import * as workingConditionView from "../sizer_create/views/workingConditionView";
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
    validator.add(sizerCreateView.DOMs.form.projectAltitude, [{
        strategy: 'isNumber',
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.projectInletPres, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.projectUnitsNum, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.projectSafetyFactor, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.projectEnvTemp, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.ratingFlow, [
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

    validator.add(sizerCreateView.DOMs.form.ratingPressure, [{
        strategy: "isNumber",
        errorMsg: {
            "cn": "请填写数字",
            "en": "Please Input Number"
        },
    }]);

    validator.add(sizerCreateView.DOMs.form.ratingTemp, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.ratingHumi, [
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

    validator.add(sizerCreateView.DOMs.form.ratingPointInletPressure, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.ratingPointInletTemp, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.ratingPointHumi, [
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

    validator.add(sizerCreateView.DOMs.form.ratingPointInletLoss, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.ratingPointOutletLoss, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.ratingPointOutPressure, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.maxFlowCoeff, [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }
    ]);

    validator.add(sizerCreateView.DOMs.form.maxPressureCoeff, [
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
sizerCreateView.DOMs.form.addEventListener("click", function(event) {
    if(event.target.matches('.card-header, .card-header *')) {
        let cardHeader = event.target.closest('.card-header');
        cardView.fold(cardHeader);
    }
});

sizerCreateView.DOMs.conditionSec.addEventListener('click', function(event) {
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

sizerCreateView.DOMs.form.addEventListener('keyup', function(event) {
    if (event.target.matches('.value-input input')) {
        sizerCreateView.clearFormInputError(event.target);
    }
});

sizerCreateView.DOMs.unitSelect.addEventListener("change", function(event) {
    renderLoading(sizerCreateView.DOMs.loadIcon);
    setupUnits();
    removeLoading(sizerCreateView.DOMs.loadIcon);
});

sizerCreateView.DOMs.uploadBtn.addEventListener("click", function(event) {
    sizerCreateView.DOMs.uploadFile.click();
});

sizerCreateView.DOMs.uploadFile.addEventListener("change", function(event) {
    let fileName = this.files[0].name;
    let translation = {
        "cn": "文件名：",
        "en": "Filename: "
    };
    sizerCreateView.DOMs.uploadLb.innerHTML = translation[lang] + fileName;
});

sizerCreateView.DOMs.checkBtn.addEventListener('click', function(event) {
    // 删除图表区域
    sizerCreateView.deleteGraphSec();
    // disable提交按钮
    disableBtn(sizerCreateView.DOMs.checkBtn);
    // loading图标
    renderLoading(sizerCreateView.DOMs.loadIcon);
    if (!formValidation()) {
        return false;
    }
    // 获取最终传输数据
    sizerCreateView.DOMs.wkConditionInput.value = JSON.stringify(workingConditionView.getConditionTablesData());

    sendCheckRequest();

});

const formValidation = function() {
    if (!validateFields()) {
        removeLoading(sizerCreateView.DOMs.loadIcon);
        ableBtn(sizerCreateView.DOMs.checkBtn);
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
    let formData = new FormData(document.querySelector(`#${sizerCreateView.DOMstrings.turboForm}`));
    let checkRequest = new Request(sizerCreateView.URLs.checkBlower, formData);

    try {
        await checkRequest.getResults();
        removeLoading(sizerCreateView.DOMs.loadIcon);
        ableBtn(sizerCreateView.DOMs.checkBtn);
        let result = checkRequest.data;
        if (result.status == "failure") {
            toastr.options = {
                timeOut: toastrTime["danger"],
                positionClass: 'toast-top-right'
            };
            toastr.error(errorCode[lang][result.errorCode]);
            return false;
        }

        sizerCreateView.generateGraph(result);
        let form = document.getElementById(sizerCreateView.DOMstrings.excelForm);
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            form.querySelector(`[name=${sizerCreateView.DOMstrings.excelField}]`).value = JSON.stringify(result);
            form.submit();
        });

        let saveBtn = document.getElementById(sizerCreateView.DOMstrings.saveBtn);
        saveBtn.addEventListener("click", function(event) {
            renderLoading(sizerCreateView.DOMs.loadIcon);
            disableBtn(saveBtn);
            sendSaveRequest(formData, saveBtn);
        });

    } catch (err) {
        removeLoading(sizerCreateView.DOMs.loadIcon);
        ableBtn(sizerCreateView.DOMs.checkBtn);
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
    let saveRequest = new Request(sizerCreateView.URLs.createSizer, formData);
    try {
        await saveRequest.getResults();
        removeLoading(sizerCreateView.DOMs.loadIcon);
        handleResponse(saveRequest.data, "createSizerSuccess", lang);
    } catch (err) {
        removeLoading(sizerCreateView.DOMs.loadIcon);
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
    let data = [
        {inletPressure: "0.988", inletTemp: "40", inletReltHumi: "90"},
        {inletPressure: "0.988", inletTemp: "20", inletReltHumi: "70"},
        {inletPressure: "0.988", inletTemp: "0", inletReltHumi: "60"},
    ];
    data.forEach(function(option) {
        ctrlAddWorkingCondition(option);
    })
};

const setupUnits = function() {
    let unitSelection = unitSelectValue(sizerCreateView.DOMs.unitSelect);
    let allUnits = document.querySelectorAll(`[${sizerCreateView.DOMstrings.unitAttribute}]`);
    for (let i =0; i < allUnits.length; i++) {
        let unitValue = allUnits[i].dataset[sizerCreateView.DOMstrings.dataAttribute];
        allUnits[i].innerHTML = "(" + unit[unitSelection][unitValue] + ")";
    }
};

setupUnits();
initTables();