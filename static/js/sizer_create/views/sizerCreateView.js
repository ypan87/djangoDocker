/**
 * Created by yifan_pan on 2019/10/15.
 */
import {language, Validation} from "../../es6/base";
import {getLang} from "../../util/util"

export const DOMs = {
    form: document.querySelector('#turboForm'),
    addCondBtn: document.querySelector('.condition-table-add'),
    condTableWrapper: document.querySelector('.condition-table-wrapper'),
    checkBtn: document.querySelector('#checkBtn'),
    loadIcon: document.querySelector('.overlay'),
    projectSec: document.querySelector('.project-sec'),
    defSec: document.querySelector('.def-sec'),
    rateSec: document.querySelector('.rate-sec'),
    conditionSec: document.querySelector('.condition-sec'),
    performanceSec: document.querySelector('.performance-sec'),
    imperialSelect: document.querySelector('#isImperial'),
    languageSelect: document.querySelector('#langSelect'),
    wkConditionInput: document.querySelector('#workingConditions'),
    unitSelect: document.querySelector('#isImperial'),
    uploadBtn: document.querySelector("#uploadBtn"),
    uploadFile: document.querySelector("#uploadFile"),
    uploadLb: document.querySelector("#uploadLb"),
};

export const DOMstrings = {
    graphSec: "graph-sec",
    effChart: "efficiencyChart",
    graphCardBody: "graphCardBody",
    turboInfo: "turboInfo",
    turboGraph: "turboGraph",
    exportExcel: "exportExcel",
    excelForm: "excelForm",
    saveBtn: "saveSizer",
    turboForm: "turboForm",
    csrfToken: "csrfmiddlewaretoken",
    excelField: "excelValue",
    unitAttribute: "data-unit",
    dataAttribute: "unit"
};

export const URLs = {
    checkBlower: "/" + getLang() + "/projects/sizers/check/",
    downloadExcel: "/" + getLang() + "/projects/sizers/excel/",
    createSizer: window.location.pathname,
};

export const Units = {
    length: "length",
    absPress: "absPress",
    temp: "temp",
    flow: "flow",
    gaugePress: "gaugePress"
};

export const colors = {
    black: "rgb(0, 0, 0)",
    red: "rgb(244,96,108)",
    green: "rgb(25,202,173)"
};

export const scrollAnimation = function(height) {
    var speed = 1600;
    $("body,html").animate({ scrollTop: height }, speed);
};

export const getFormInputExceptWorkingCondition = function() {
    let projectData = getSectionData(DOMs.projectSec);
    let defData = getSectionData(DOMs.defSec);
    let rateData = getSectionData(DOMs.rateSec);
    let performanceData = getSectionData(DOMs.performanceSec);
    let imperialSelectData = getSelectData(DOMs.imperialSelect);
    return Object.assign(projectData, defData, rateData, performanceData, imperialSelectData);
};

export const generateGraph = function(data) {
    insertGraphSection();
    insertEffGraph(data);
    insertTurboSelectionTable(data);
    insertTurboSpecificsTable(data);
    insertTurboGraph(data);
    let height = $('#' + DOMstrings.graphSec).offset().top;
    scrollAnimation(height);
};

export const deleteGraphSec = function() {
    let graphSec = document.querySelector("#" + DOMstrings.graphSec);
    if (graphSec) {
        graphSec.parentElement.removeChild(graphSec);
    }
};

export const clearFormInputError = function(input) {
    var inputError = input.parentElement.querySelector(".input-error");
    if (inputError) {
        inputError.innerHTML = '';
        if (!inputError.classList.contains('hidden')) {
            inputError.classList.add('hidden');
        }
    }
};

const getSectionData = function(section) {
    let inputs = section.querySelectorAll('input');
    let data = {};
    for (let i = 0; i < inputs.length; i++) {
        let input = inputs[i];
        if (input.value == "") continue;
        data[input.name] = input.value;
    }
    return data;
};

const getSelectData = function(select) {
    let index = select.selectedIndex;
    return {
        [select.name]: select[index].value
    }
};

const insertGraphSection = function() {
    let lang = getLang();
    let markup = `
        <div class="row" id="graph-sec">
            <div class="col-12">
                <div class="card">
                    <div class="card-header card-header-active">
                        <div class="d-flex justify-content-between">
                            <div>
                                ${language[lang]["blowerSelection"]}                           
                            </div>
                            <div class="d-flex justify-content-between">
                                <form method="post" action="${URLs.downloadExcel}" id="excelForm">
                                    <button type="submit" class="btn btn-light mr-24">${language[lang]["outputExcel"]}</button>
                                    <input type="hidden" name="csrfmiddlewaretoken">
                                    <input type="hidden" name="excelValue">
                                </form>
                                <button type="submit" class="btn btn-light ml-24" id="saveSizer">${language[lang]["createSizer"]}</button>
                            </div>
                        </div>
                    </div>
    
                    <div class="card-body" id="graphCardBody">
                        <div class="row">
                            <div class="col-lg-6">
                                <canvas id="efficiencyChart" height="275px"></canvas>
                            </div>
                            <div class="col-lg-6" id="turboInfo"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div> 
    `;
    DOMs.form.insertAdjacentHTML("afterend", markup);
    let excelForm = document.getElementById(DOMstrings.excelForm);
    excelForm.querySelector(`[name=${DOMstrings.csrfToken}]`).value = DOMs.form.csrfmiddlewaretoken.value;
};

const insertEffGraph = function(data) {
    let lang = getLang();
    let ctx = document.getElementById(DOMstrings.effChart).getContext('2d');
    let datasets = [], singleData, i;

    // 添加测试点数据
    for (i = 0; i < data.baseTableData.length; i++) {
        singleData = getGraphData({
            data: data.baseTableData[i],
            category: "test",
            label: language[lang]["testingCurve"] + " " + i,
            color: colors.black
        });
        datasets.push(singleData);
    }

    // 添加工况曲线数据
    for (i = 0; i < data.normalTableData.length; i++) {
        singleData = getGraphData({
            data: data.normalTableData[i],
            category: "condition",
            label: language[lang]["wkCurve"] + " " + i,
            color: colors.red,
        });
        datasets.push(singleData);
    }

    // 添加效率曲线数据
    for (i = 0; i < data.efficiencyTableData.length; i++) {
        singleData = getGraphData({
            data: data.efficiencyTableData[i],
            category: "efficiency",
            label: language[lang]["effCurve"] + " " + i,
            color: colors.green
        });
        datasets.push(singleData);
    }

    // 添加额定工况点数据
    singleData = getGraphData({
        data: [data.ratedTableData],
        category: "rating",
        label: language[lang]["ratingPoint"],
        color: colors.red
    });
    datasets.push(singleData);

    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: language[lang]["flowCoeff"]
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: false
                    },
                    position: 'left',
                    id: 'y-axis-1',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: language[lang]["pressCoeff"]
                    }
                }]
            },
            title: {
                display: true,
                text: language[lang]["effGraph"]
            },
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 20,
                    fontSize: 8
                }
            },
        }
    });
};

const getGraphData = function(option) {
    let dataPoints = [];
    if (!option.data) return dataPoints;
    for (let point of option.data) {
        dataPoints.push({
            x: point[0],
            y: point[1]
        });
    }
    return {
        label: option.label,
        data: dataPoints,
        pointStyle: option.category == "rating" ? "triangle" : "circle",
        borderColor: option.color,
        backgroundColor: option.color,
        borderWidth: option.category == "rating" ? 5 : 2,
        showLine: option.category != "design",
        fill: false,
        yAxisID: option.category == "power" ? 'y-axis-2' : "y-axis-1",
        pointRadius: 2
    };
};

const insertTurboSelectionTable = function(data) {
    let lang = getLang();
    let turboData = data.tableData;
    let markup = `
        <div class="table-responsive">
            <table class="table table-bordered table-striped text-center">
                <tr>
                    <th>${language[lang]["blowerCategory"]}</th>
                    <th>${language[lang]["cutBack"]}</th>
                </tr>

                <tr>
                    <td>
                        ${turboData.turbo}
                    </td>
                    <td>
                        ${turboData.cutBack}
                    </td>
                </tr>
            </table>
        </div> 
    `;
    document.getElementById(DOMstrings.turboInfo).insertAdjacentHTML("beforeend", markup);
};

const insertTurboSpecificsTable = function(data) {
    let markup = "";
    for (let i = 0; i < data.tableData.conditions.length; i++) {
        markup += getTurboSpecificsHTML(data.tableData.conditions[i], data.tableData.turbo);
    }
    markup = `
        <div class="row">
    ` + markup + `</div>`;
    document.getElementById(DOMstrings.graphCardBody).insertAdjacentHTML('beforeend', markup);
};

const getTurboSpecificsHTML = function(conditions, turbo) {
    let lang = getLang();
    let template = "";
    for (let i = 0; i < conditions.dataSet.length; i++) {
        let point = conditions.dataSet[i];
        template += `
            <tr>
                <td colspan="4">${point.relativeFlow} %</td>
                <td colspan="1">${point.outletPress}</td>
                <td colspan="1">${point.flowAmb}</td>
                <td colspan="1">${point.shaftPower}</td>
                <td colspan="1">${point.wirePower}</td>
            </tr>
        `
    }

    template = `
        <div class="table-responsive col-6">
            <table class="table table-bordered table-striped text-center final-table">
                <tr>
                    <td colspan="4">${language[lang]["blowerCategory"]}：${turbo}</td>
                    <td colspan="4">${conditions.temp}&#8451;/${conditions.humidity}%</td>
                </tr>
                <tr>
                    <td colspan="4">${language[lang]["inletPressure"]}</td>
                    <td colspan="4">${conditions.baraPressure} bara</td>
                </tr>
                <tr>
                    <td colspan="4">${language[lang]["dutyRelativeFlow"]}</td>
                    <td colspan="1">ΔP</td>
                    <td colspan="1">${language[lang]["flow"]}</td>
                    <td colspan="1">${language[lang]["shaftPower"]}</td>
                    <td colspan="1">${language[lang]["wirePower"]}</td>
                </tr>
                <tr>
                    <td colspan="4">%</td>
                    <td colspan="1">barG</td>
                    <td colspan="1">m<sup>3</sup>/h</td>
                    <td colspan="1">kW</td>
                    <td colspan="1">kW</td>
                </tr>  
    `
    + template + `
            </table>
        </div>
    `;
    return template;
};

const insertTurboGraph = function(data) {
    let lang = getLang();
    let templates = "";
    for (let i = 0; i < data.conditions.length; i++) {
        templates += `                        
        <div class="col-lg-6">
            <canvas height="275px"></canvas>
        </div>`;
    }
    templates = `
        <div class="row" id="turboGraph">
    ` + templates + `</div>`;

    document.getElementById(DOMstrings.graphCardBody).insertAdjacentHTML('beforeend', templates);
    let canvasCollection = document.getElementById(DOMstrings.turboGraph).querySelectorAll('canvas');
    for (let i = 0; i < data.conditions.length; i++) {
        let index = i + 1;
        insertSingleTurboGraph({
            data: data.conditions[i],
            ctx: canvasCollection[i].getContext("2d"),
            title: language[lang]["wkCurve"] + index,
        });
    }
};

const insertSingleTurboGraph = function(option) {
    let datasets = [];
    let condData = option.data[0];
    let powerData = option.data[1];
    let designData = option.data[2];
    let lang = getLang();

    for (let i = 0; i < condData.length; i++) {
        let index = i + 1;
        let singleData = getGraphData({
            data: condData[i],
            category: "condition",
            label:  language[lang]["pvCurve"]+ " " + index,
            color: colors.black
        });
        datasets.push(singleData);
    }

    let powerGraphData = getGraphData({
        data: powerData,
        category: "power",
        label: language[lang]["pShaftCurve"],
        color: colors.green
    });
    datasets.push(powerGraphData);

    let designGraphData = getGraphData({
        data: designData,
        category: "design",
        label: language[lang]["pvForDP"],
        color: colors.red
    });
    datasets.push(designGraphData);

    // 创建图表
    return new Chart(option.ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: language[lang]["flow"] + ' - m3/h'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    position: 'left',
                    id: 'y-axis-1',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: language[lang]["voltageRise"] + ' - mbarg'
                    }
                }, {
                    ticks: {
                        beginAtZero: true
                    },
                    position: 'right',
                    id: 'y-axis-2',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: language[lang]["shaftPower"] + ' - kw'
                    }
                }]
            },
            title: {
                display: true,
                text: language[lang]["pvShaftCurve"] + option.title + '：'
            },
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 20,
                    fontSize: 8
                }
            },
        }
    });
};
