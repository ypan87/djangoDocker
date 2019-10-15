/**
 * Created by yifan_pan on 2019/10/15.
 */
import {DOMs, Units} from "./sizerCreateView";
import {unitSelectValue} from "../../util/util";
import {language, unit} from "../../es6/base";
import {getLang} from "../../util/util";

let lang = getLang();

export class conditionTables {
    constructor() {
        this.condTables = [];
    }

    addWkTable(wkCond, validator) {
        if (this.condTables.length > 0) {
            let index = this.condTables.findIndex(function(el) {
                return el.dataset.tableid == wkCond.id;
            });
            let selectedTable = this.condTables.splice(index, 1)[0];
            DOMs.condTableWrapper.insertAdjacentElement('beforeend', selectedTable);
            return;
        }

        let markup = `
            <div class="col-sm-4" data-tableid=${wkCond.id}>
                <table class="table table-bordered table-striped text-center mt-24 condition-table">
                    <tr>
                        <th scope="col" colspan="3" class="condition-table-header">
                            ${language[lang]["duty"]}
                            <button type="button" class="close condition-table-close">
                                <span>&times;</span>
                            </button>
                        </th>
                    </tr>
                    <tr class="general">
                        <th scope="row">
                            ${language[lang]["dutyInletPressure"]} 
                            <span data-unit=${Units.absPress}>
                                ${unit[unitSelectValue(DOMs.unitSelect)][Units.absPress]}
                            </span>
                        </th>
                        <td colspan="2">
                            <div class="value-input">
                                <input type="text" class="form-control" value=${wkCond.inletPressure || ""}>
                                <div class="input-error hidden"></div>
                            </div>
                        </td>
                    </tr>
                    <tr class="general">
                        <th scope="row">
                            ${language[lang]["dutyInletTemp"]}
                            <span data-unit=${Units.temp}>
                                ${unit[unitSelectValue(DOMs.unitSelect)][Units.temp]}
                            </span>
                        </th>
                        <td colspan="2">
                            <div class="value-input">
                                <input type="text" class="form-control" value=${wkCond.inletTemp || ""}>
                                <div class="input-error hidden"></div>
                            </div>
                        </td>
                    </tr>
                    <tr class="general">
                        <th scope=row>
                            ${language[lang]["dutyRelativeHumidity"]}
                            <span>(%)</span>
                        </th>
                        <td colspan="2">
                            <div class="value-input">
                                <input type="text" class="form-control" value=${wkCond.inletReltHumi || ""}>
                                <div class="input-error hidden"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="3"></td>
                    </tr>
                    <tr class="pointHead">
                        <th scope="col">
                            ${language[lang]["dutyRelativeFlow"]}
                            <span>(%)</span>
                        </th>
                        <th scope="col">
                            ${language[lang]["dutyPressure"]}
                            <span data-unit="${Units.gaugePress}">
                                ${unit[unitSelectValue(DOMs.unitSelect)][Units.gaugePress]}
                            </span>
                        </th>
                        <th scope="col">
                            ${language[lang]["dutyOperation"]}
                        </th>
                    </tr>
                    <tr class="pointAdd">
                        <td>
                            <input type="text" class="form-control">
                        </td>
                        <td>
                            <input type="text" class="form-control">
                        </td>
                        <td>
                            <span class="row-add">
                                <button type="button" class="btn btn-outline-success">
                                    ${language[lang]["dutyAdd"]}
                                </button>
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
        `;
        DOMs.condTableWrapper.insertAdjacentHTML('beforeend', markup);
        let newTable = document.querySelector(`[data-tableid="${wkCond.id}"]`);
        let inputs = newTable.querySelectorAll('input');
        validator.add(inputs[0], [{
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }]);
        validator.add(inputs[1], [{
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        }]);
        validator.add(inputs[2], [
            {
                strategy: "isNumber",
                errorMsg: {
                    "cn": "请填写数字",
                    "en": "Please Input Number"
                },
            },
            {
                strategy: "maxValue:100",
                errorMsg: {
                    "cn": "请填写小于100的数字",
                    "en": "Please Input Number Smaller Than 100"
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
        let addRow = newTable.querySelector(`.pointAdd`);
        if (wkCond.points) {
            for (let i = 0; i < wkCond.points.length; i++) {
                addWkPoint(wkCond.points[i], addRow, validator);
            }
        }
    }

    deleteWkTable(table, validator) {
        let inputs = table.querySelectorAll('input');
        for (let i = 0; i < inputs.length; i++) {
            validator.remove(inputs[i]);
        }
        this.condTables.push(table);
        table.parentElement.removeChild(table);
    }
}

export const addWkPoint = function(elem, addRow, validator) {
    let markup = `
    <tr class="point">
        <td>
            <div class="value-input">
                <input type="text" class="form-control" value="${elem.flow}">
                <div class="input-error hidden"></div>
            </div>
        </td>
        <td>
            <div class="value-input">
                <input type="text" class="form-control" value="${elem.pressure}">
                <div class="input-error hidden"></div>
            </div>
        </td>
        <td>
            <span class="row-del">
                <button type="button" class="btn btn-outline-danger">${language[lang]["dutyDelete"]}</button>
            </span>
        </td>
    </tr>`;

    addRow.insertAdjacentHTML("beforebegin", markup);

    let newRow = addRow.previousSibling;
    let inputs = newRow.querySelectorAll('input');
    validator.add(inputs[0], [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        },
        {
            strategy: "maxValue:100",
            errorMsg: {
                "cn": "请填写小于100的数字",
                "en": "Please Input Number Smaller Than 100"
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
    validator.add(inputs[1], [
        {
            strategy: "isNumber",
            errorMsg: {
                "cn": "请填写数字",
                "en": "Please Input Number"
            },
        },
    ]);
};

export const deleteWkPoint = function(row, validator) {
    let inputs = row.querySelectorAll('input');
    validator.remove(inputs[0]);
    validator.remove(inputs[1]);
    row.parentElement.removeChild(row);
};

export const getRowInput = function(addRow) {
    let inputs = addRow.querySelectorAll('input');
    return {
        flow: inputs[0].value,
        pressure: inputs[1].value
    };
};

export const clearRowInput = function(addRow) {
    let inputs = addRow.querySelectorAll('input');
    inputs[0].value = "";
    inputs[1].value = "";
};

export const getConditionTablesData = function() {
    let tables = DOMs.conditionSec.querySelectorAll('[data-tableid]');
    let tablesData = [];
    for (let i = 0; i < tables.length; i++) {
        let table = tables[i];
        let tableData = getTableData(table);
        tablesData.push(tableData);
    }
    return tablesData;
};

const getTableData = function(table) {
    const tableData = {};

    const generalRows = table.querySelectorAll('tr.general');
    tableData["pressure"] = generalRows[0].querySelector('input').value;
    tableData["temp"] = generalRows[1].querySelector('input').value;
    tableData["humi"] = generalRows[2].querySelector('input').value;

    let pointRows = table.querySelectorAll("tr.point");
    let points = [];
    for (let i = 0; i < pointRows.length; i++) {
        let inputs = pointRows[i].querySelectorAll('input');
        points.push({flow: inputs[0].value, pressure: inputs[1].value});
    }

    tableData["points"] = points;

    return tableData;
};
