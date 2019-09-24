/**
 * Created by yifan_pan on 2019/9/11.
 */
var baseController = (function(){

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
        this.url = url;
        this.data = data;
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
        getCookie: function(name) {
            return getCookie(name);
        }
    }
})();

var baseView = (function(baseCtrl) {
    var DOMs = {
        form: document.querySelector('#turboForm'),
        addCondBtn: document.querySelector('.condition-table-add'),
        condTableWrapper: document.querySelector('.condition-table-wrapper'),
        checkBtn: document.querySelector('#checkBtn'),
        loadIcon: document.querySelector('.wrapper'),
        projectSec: document.querySelector('.project-sec'),
        defSec: document.querySelector('.def-sec'),
        rateSec: document.querySelector('.rate-sec'),
        conditionSec: document.querySelector('.condition-sec'),
        performanceSec: document.querySelector('.performance-sec'),
        imperialSelect: document.querySelector('#isImperial'),
        languageSelect: document.querySelector('#langSelect'),
        wkConditionInput: document.querySelector('#workingConditions'),
    };

    var DOMStrings = {
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
    };

    var URLs = {
        checkBlower: "/projects/sizers/check/",
        downloadExcel: "/projects/sizers/excel/",
        createSizer: window.location.pathname,
    };

    var colors = {
        black: "rgb(0, 0, 0)",
        red: "rgb(244,96,108)",
        green: "rgb(25,202,173)"
    };

    var getSectionData = function(section) {
        var inputs = section.querySelectorAll('input');
        var data = {};
        for (var i = 0; i < inputs.length; i++) {
            var input = inputs[i];
            if (input.value == "") continue;
            data[input.name] = input.value;
        }
        return data;
    };

    var getSelectData = function(select) {
        var index = select.selectedIndex;
        return {
            [select.name]: select[index].value
        }
    };

    var insertGraphSection = function() {
        var markup = `
            <div class="row" id="graph-sec">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header card-header-active">
                            <div class="d-flex justify-content-between">
                                <div>
                                    鼓风机选择                            
                                </div>
                                <div class="d-flex justify-content-between">
                                    <form method="post" action="${URLs.downloadExcel}" id="excelForm">
                                        <button type="submit" class="btn btn-light mr-24">输出excel</button>
                                        <input type="hidden" name="csrfmiddlewaretoken">
                                        <input type="hidden" name="excelValue">
                                    </form>
                                    <button type="submit" class="btn btn-light ml-24" id="saveSizer">创建选型</button>
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
        var excelForm = document.getElementById(DOMStrings.excelForm);
        excelForm.querySelector(`[name=${DOMStrings.csrfToken}]`).value = baseCtrl.getCookie("csrftoken");
    };

    var insertEffGraph = function(data) {
        var ctx = document.getElementById(DOMStrings.effChart).getContext('2d');
        var datasets = [], singleData, i;

        // 添加测试点数据
        for (i = 0; i < data.baseTableData.length; i++) {
            singleData = getGraphData({
                data: data.baseTableData[i],
                category: "test",
                label: "测试曲线" + i,
                color: colors.black
            });
            datasets.push(singleData);
        }

        // 添加工况曲线数据
        for (i = 0; i < data.normalTableData.length; i++) {
            singleData = getGraphData({
                data: data.normalTableData[i],
                category: "condition",
                label: "工况曲线" + i,
                color: colors.red,
            });
            datasets.push(singleData);
        }

        // 添加效率曲线数据
        for (i = 0; i < data.efficiencyTableData.length; i++) {
            singleData = getGraphData({
                data: data.efficiencyTableData[i],
                category: "efficiency",
                label: "效率曲线" + i,
                color: colors.green
            });
            datasets.push(singleData);
        }

        // 添加额定工况点数据
        singleData = getGraphData({
            data: [data.ratedTableData],
            category: "rating",
            label: "额定工况点",
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
                            labelString: '最大流量系数'
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
                            labelString: '压力系数'
                        }
                    }]
                },
                title: {
                    display: true,
                    text: '效率曲线'
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

    var getGraphData = function(option) {
        var dataPoints = [];
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

    var insertTurboSelectionTable = function(data) {
        var turboData = data.tableData;
        var markup = `
            <div class="table-responsive">
                <table class="table table-bordered table-striped text-center">
                    <tr>
                        <th>鼓风机型号</th>
                        <th>叶轮机切顶</th>
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
        document.getElementById(DOMStrings.turboInfo).insertAdjacentHTML("beforeend", markup);
    };

    var insertTurboSpecificsTable = function(data) {
        var markup = "";
        for (var i = 0; i < data.tableData.conditions.length; i++) {
            markup += getTurboSpecificsHTML(data.tableData.conditions[i], data.tableData.turbo);
        }
        markup = `
            <div class="row">
        ` + markup + `</div>`;
        document.getElementById(DOMStrings.graphCardBody).insertAdjacentHTML('beforeend', markup);
    };

    var getTurboSpecificsHTML = function(conditions, turbo) {
        var template = "";
        for (var i = 0; i < conditions.dataSet.length; i++) {
            var point = conditions.dataSet[i];
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
                        <td colspan="4">风机型号：${turbo}</td>
                        <td colspan="4">${conditions.temp}&#8451;/${conditions.humidity}%</td>
                    </tr>
                    <tr>
                        <td colspan="4">进气压力</td>
                        <td colspan="4">${conditions.baraPressure} bara</td>
                    </tr>
                    <tr>
                        <td colspan="4">相对流量</td>
                        <td colspan="1">ΔP</td>
                        <td colspan="1">流量</td>
                        <td colspan="1">轴功率</td>
                        <td colspan="1">进线功率</td>
                    </tr>              
        `
        + template + `
                </table>
            </div>
        `;
        return template;
    };

    var insertTurboGraph = function(data) {
        var templates = "";
        for (var i = 0; i < data.conditions.length; i++) {
            templates += `                        
            <div class="col-lg-6">
                <canvas height="275px"></canvas>
            </div>`;
        }
        templates = `
            <div class="row" id="turboGraph">
        ` + templates + `</div>`;

        document.getElementById(DOMStrings.graphCardBody).insertAdjacentHTML('beforeend', templates);
        var canvasCollection = document.getElementById(DOMStrings.turboGraph).querySelectorAll('canvas');
        for (i = 0; i < data.conditions.length; i++) {
            var index = i + 1;
            insertSingleTurboGraph({
                data: data.conditions[i],
                ctx: canvasCollection[i].getContext("2d"),
                title: "工况曲线" + index,
            });
        }
    };

    var insertSingleTurboGraph = function(option) {
        var datasets = [];
        var condData = option.data[0];
        let powerData = option.data[1];
        let designData = option.data[2];

        for (let i = 0; i < condData.length; i++) {
            var index = i + 1;
            let singleData = getGraphData({
                data: condData[i],
                category: "condition",
                label: "流量压升曲线" + index,
                color: colors.black
            });
            datasets.push(singleData);
        }

        var powerGraphData = getGraphData({
            data: powerData,
            category: "power",
            label: "流量轴功率曲线",
            color: colors.green
        });
        datasets.push(powerGraphData);

        let designGraphData = getGraphData({
            data: designData,
            category: "design",
            label: "设计点流量压升",
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
                            labelString: '流量 - m3/h'
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
                            labelString: '压升 - mbarg'
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
                            labelString: '轴功率 - kw'
                        }
                    }]
                },
                title: {
                    display: true,
                    text: '流量压力曲线及轴功率' + option.title + '：'
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

    return {
        getDOMS: function() {
            return DOMs;
        },
        getDOMStrings: function() {
            return DOMStrings;
        },
        renderErrorTip: function() {
            var markup = `
                <div class="alert alert-danger error-tip">
                    输入有错误，请修改错误后再提交
                </div>
            `;
            DOMs.form.insertAdjacentHTML("beforebegin", markup);
            var height = $(".error-tip").offset().top;
            this.scrollAnimation(height);
        },
        deleteErrorTip: function() {
            var error = document.querySelector('.error-tip');
            if (error) {
                error.parentElement.removeChild(error);
            }
        },
        scrollAnimation: function(height) {
            var speed = 1600;
            $("body,html").animate({ scrollTop: height }, speed);
        },
        clearFormInputError: function(input) {
            var inputError = input.parentElement.querySelector(".input-error");
            if (inputError) {
                inputError.innerHTML = '';
                if (!inputError.classList.contains('hidden')) {
                    inputError.classList.add('hidden');
                }
            }
        },
        diableCheckBtn: function() {
            DOMs.checkBtn.disabled = true;
        },
        ableCheckBtn: function() {
            DOMs.checkBtn.disabled = false;
        },
        diableSubBtn: function() {
            DOMs.subBtn.disabled = true;
        },
        ableSubBtn: function() {
            DOMs.subBtn.disabled = false;
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
        getFormInputExceptWorkingCondition: function() {
            var projectData = getSectionData(DOMs.projectSec);
            var defData = getSectionData(DOMs.defSec);
            var rateData = getSectionData(DOMs.rateSec);
            var performanceData = getSectionData(DOMs.performanceSec);
            var imperialSelectData = getSelectData(DOMs.imperialSelect);
            return Object.assign(projectData, defData, rateData, performanceData, imperialSelectData);
        },
        generateGraph: function(data) {
            insertGraphSection();
            insertEffGraph(data);
            insertTurboSelectionTable(data);
            insertTurboSpecificsTable(data);
            insertTurboGraph(data);
            var height = $('#' + DOMStrings.graphSec).offset().top;
            this.scrollAnimation(height);
        },
        deleteGraphSec: function() {
            var graphSec = document.querySelector("#" + DOMStrings.graphSec);
            if (graphSec) {
                graphSec.parentElement.removeChild(graphSec);
            }
        },
        getURLs: function() {
            return URLs;
        }
    }
})(baseController);

var cardController = (function() {
    return {
        fold: function(cardHeader) {
            if (!cardHeader) return;
            var cardBody = cardHeader.nextElementSibling;
            var triIcon = cardHeader.querySelector('.card-header-icon');
            if (triIcon) {
                triIcon.classList.toggle('icon-rotate');
            }
            cardBody.classList.toggle('card-body-collapsed');
            cardHeader.classList.toggle('card-header-active');
        }
    }
})();

var validateCtrl = (function(baseView) {
    var form = baseView.getDOMS().form;

    var validator = new Validator();

    validator.add(form.projectAltitude, [{
        strategy: 'isNumber',
        errorMsg: '请填写数字',
    }]);

    validator.add(form.projectInletPres, [{
        strategy: "isNumber",
        errorMsg: '请填写数字',
    }]);

    validator.add(form.projectUnitsNum, [{
        strategy: "isNumber",
        errorMsg: '请填写数字',
    }]);

    validator.add(form.projectSafetyFactor, [{
        strategy: "isNumber",
        errorMsg: '请填写数字',
    }]);

    validator.add(form.projectEnvTemp, [{
        strategy: "isNumber",
        errorMsg: '请填写数字',
    }]);

    validator.add(form.ratingFlow, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        },
        {
            strategy: "minValue:0",
            errorMsg: '请填写大于0的数字',
        }
    ]);

    validator.add(form.ratingPressure, [{
        strategy: "isNumber",
        errorMsg: '请填写数字',
    }]);

    validator.add(form.ratingTemp, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.ratingHumi, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        },
        {
            strategy: "minValue:0",
            errorMsg: '请填写大于0的数字',
        },
        {
            strategy: "maxValue:100",
            errorMsg: '请填写小于100的数字',
        }
    ]);

    validator.add(form.ratingPointInletPressure, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.ratingPointInletTemp, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.ratingPointHumi, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        },
        {
            strategy: "minValue:0",
            errorMsg: '请填写大于0的数字',
        },
        {
            strategy: "maxValue:100",
            errorMsg: '请填写小于100的数字',
        }
    ]);

    validator.add(form.ratingPointInletLoss, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.ratingPointOutletLoss, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.ratingPointOutPressure, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.maxFlowCoeff, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    validator.add(form.maxPressureCoeff, [
        {
            strategy: "isNumber",
            errorMsg: '请填写数字',
        }
    ]);

    var displayError = function(errorMsg) {
        let inputError = this.parentElement.getElementsByClassName('input-error')[0];
        if (!inputError) return;
        inputError.innerHTML = errorMsg;
        if (inputError.classList.contains('hidden')) {
            inputError.classList.remove('hidden');
        }
    };

    return {
        addValidatorRule: function(dom, rules) {
            validator.add(dom, rules);
        },
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
        removeValidatorRule: function(dom) {
            validator.remove(dom);
        }
    }
})(baseView);

var workingConditionController = (function() {
    // 保存新建的Condition
    var wkCondsAll = [];
    // 保存正在使用的Condition
    var wkCondsInUse = [];
    // 保存可以使用的id
    var ids = [];

    var findIdIndexInAry = function(ary, id) {
        return ary.findIndex(function(el) {
            return el == id;
        });
    };

    return {
        addWkCond: function(option) {
            var id;
            // 如果还有id可以使用，则找到对应的Condition然后返回
            if (ids.length > 0) {
                id = ids.shift();
            } else {
                // 如果没有id可以使用，则新建新的Condition返回
                var condsLength = wkCondsAll.length;
                if (condsLength == 0) {
                    id = 0;
                } else {
                    id = wkCondsAll[condsLength - 1] + 1;
                }
                wkCondsAll.push(id);
            }
            wkCondsInUse.push(id);

            return {
                id: id,
                inletPressure: option ? option.inletPressure : null,
                inletTemp: option ? option.inletTemp : null,
                inletReltHumi: option ? option.inletReltHumi : null,
                points: option && option.points ? option.points : [
                    {flow: 100, pressure: 0.6},
                    {flow: 90, pressure: 0.6},
                    {flow: 80, pressure: 0.6},
                    {flow: 70, pressure: 0.6},
                    {flow: 60, pressure: 0.6},
                    {flow: 45, pressure: 0.6},
                ]
            };
        },
        deleteWkCond: function(id) {
            ids.push(id);
            var index = findIdIndexInAry(wkCondsInUse, id);
            wkCondsInUse.splice(index, 1);
        },
        getWkCondInUse: function() {
            return wkCondsInUse.length;
        }
    }
})();

var workingConditionViewController = (function(baseView, vldCtrl) {
    var condTables = [];
    var DOMs = baseView.getDOMS();

    var getTableData = function(table) {
        var tableData = {};

        var generalRows = table.querySelectorAll('tr.general');
        tableData["pressure"] = generalRows[0].querySelector('input').value;
        tableData["temp"] = generalRows[1].querySelector('input').value;
        tableData["humi"] = generalRows[2].querySelector('input').value;

        var pointRows = table.querySelectorAll("tr.point");
        points = [];
        for (var i = 0; i < pointRows.length; i++) {
            var inputs = pointRows[i].querySelectorAll('input');
            points.push({flow: inputs[0].value, pressure: inputs[1].value});
        }

        tableData["points"] = points;

        return tableData;
    };

    return {
        addWkTable: function(wkCond) {
            if (condTables.length > 0) {
                var index = condTables.findIndex(function(el) {
                    return el.dataset.tableid == wkCond.id;
                });
                var selectedTable = condTables.splice(index, 1)[0];
                DOMs.condTableWrapper.insertAdjacentElement('beforeend', selectedTable);
                return;
            }

            var markup = `
                <div class="col-sm-4" data-tableid=${wkCond.id}>
                    <table class="table table-bordered table-striped text-center mt-24 condition-table">
                        <tr>
                            <th scope="col" colspan="3" class="condition-table-header">
                                工况
                                <button type="button" class="close condition-table-close">
                                    <span>&times;</span>
                                </button>
                            </th>
                        </tr>
                        <tr class="general">
                            <th scope="row">系统进口压力</th>
                            <td colspan="2">
                                <div class="value-input">
                                    <input type="text" class="form-control" value=${wkCond.inletPressure || ""}>
                                    <div class="input-error hidden"></div>
                                </div>
                            </td>
                        </tr>
                        <tr class="general">
                            <th scope="row">进气温度</th>
                            <td colspan="2">
                                <div class="value-input">
                                    <input type="text" class="form-control" value=${wkCond.inletTemp || ""}>
                                    <div class="input-error hidden"></div>
                                </div>
                            </td>
                        </tr>
                        <tr class="general">
                            <th scope=row>进气相对湿度</th>
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
                            <th scope="col">相对流量</th>
                            <th scope="col">压力</th>
                            <th scope="col">操作</th>
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
                                    <button type="button" class="btn btn-outline-success">添加</button>
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
            `;
            DOMs.condTableWrapper.insertAdjacentHTML('beforeend', markup);
            var newTable = document.querySelector(`[data-tableid="${wkCond.id}"]`);
            var inputs = newTable.querySelectorAll('input');
            vldCtrl.addValidatorRule(inputs[0], [{
                strategy: "isNumber",
                errorMsg: "请填写数字"
            }]);
            vldCtrl.addValidatorRule(inputs[1], [{
                strategy: "isNumber",
                errorMsg: "请填写数字"
            }]);
            vldCtrl.addValidatorRule(inputs[2], [
                {
                    strategy: "isNumber",
                    errorMsg: "请填写数字"
                },
                {
                    strategy: "maxValue:100",
                    errorMsg: "请填写小于100的数字"
                },
                {
                    strategy: "minValue:0",
                    errorMsg: "请填写大于0的数字"
                }
            ]);
            var addRow = newTable.querySelector(`.pointAdd`);
            if (wkCond.points) {
                for (var i = 0; i < wkCond.points.length; i++) {
                    this.addWkPoint(wkCond.points[i], addRow);
                }
            }
        },
        deleteWkTable: function(table) {
            var inputs = table.querySelectorAll('input');
            for (var i = 0; i < inputs.length; i++) {
                vldCtrl.removeValidatorRule(inputs[i]);
            }
            condTables.push(table);
            table.parentElement.removeChild(table);
        },
        addWkPoint(elem, addRow) {
            var markup = `
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
                        <button type="button" class="btn btn-outline-danger">删除</button>
                    </span>
                </td>
            </tr>`;

            addRow.insertAdjacentHTML("beforebegin", markup);

            var newRow = addRow.previousSibling;
            var inputs = newRow.querySelectorAll('input');
            vldCtrl.addValidatorRule(inputs[0], [
                {
                    strategy: "isNumber",
                    errorMsg: "请填写数字"
                },
                {
                    strategy: "maxValue:100",
                    errorMsg: "请填写小于100的数字"
                },
                {
                    strategy: "minValue:0",
                    errorMsg: "请填写大于0的数字"
                }
            ]);
            vldCtrl.addValidatorRule(inputs[1], [
                {
                    strategy: "isNumber",
                    errorMsg: "请填写数字"
                },
            ]);
        },
        deleteWkPoint(row) {
            var inputs = row.querySelectorAll('input');
            vldCtrl.removeValidatorRule(inputs[0]);
            vldCtrl.removeValidatorRule(inputs[1]);
            row.parentElement.removeChild(row);
        },
        getRowInput: function(addRow) {
            var inputs = addRow.querySelectorAll('input');
            return {
                flow: inputs[0].value,
                pressure: inputs[1].value
            };
        },
        clearRowInput: function(addRow) {
            var inputs = addRow.querySelectorAll('input');
            inputs[0].value = "";
            inputs[1].value = "";
        },
        getConditionTablesData: function() {
            var tables = DOMs.conditionSec.querySelectorAll('[data-tableid]');
            var tablesData = [];
            for (var i = 0; i < tables.length; i++) {
                var table = tables[i];
                var tableData = getTableData(table);
                tablesData.push(tableData);
            }
            return tablesData
        }
    }
})(baseView, validateCtrl);

var controller = (function(baseView, baseCtrl, cardCtrl, wkCondCtrl, wkViewCtrl, vldCtrl) {

    var setupEventListeners = function() {
        var DOM = baseView.getDOMS();
        var DOMStrings = baseView.getDOMStrings();
        var URLs = baseView.getURLs();
        // 表格中card折叠
        DOM.form.addEventListener('click', function(event) {
            if(event.target.matches('.card-header, .card-header *')) {
                var cardHeader = event.target.closest('.card-header');
                cardCtrl.fold(cardHeader);
            }
        });

        // 工况卡片事件
        DOM.conditionSec.addEventListener('click', function(event) {
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

        // 键盘输入
        DOM.form.addEventListener('keyup', function(event) {
            if (event.target.matches('.value-input input')) {
                clearFormInputError(event);
            }
        });

        // 查看性能曲线
        DOM.checkBtn.addEventListener('click', function(event) {
            // 删除图表区域
            baseView.deleteGraphSec();
            // disable提交按钮
            baseView.diableCheckBtn();
            // loading图标
            baseView.renderLoading();
            if (!formValidation()) {
                baseView.removeLoading();
                baseView.ableCheckBtn();
                return false;
            }
            // 获取最终传输数据
            DOM.wkConditionInput.value = JSON.stringify(wkViewCtrl.getConditionTablesData());
            var formData = $(`#${DOMStrings.turboForm}`).serialize();
            var sizerRequester = baseCtrl.createRequester(URLs.checkBlower, formData);
            var promise = sizerRequester.ajaxRequest();

            promise.then(function (result) {
                if (result.status == "failure") {
                    toastr.options = {
                        timeOut: 200,
                        positionClass: 'toast-top-right'
                    };
                    toastr.error(result.errorCode);
                    return;
                }
                baseView.generateGraph(result);
                baseView.removeLoading();
                baseView.ableCheckBtn();
                var form = document.getElementById(DOMStrings.excelForm);
                form.addEventListener('submit', function(event) {
                    event.preventDefault();
                    form.querySelector(`[name=${DOMStrings.excelField}]`).value = JSON.stringify(result);
                    form.submit();
                });
                var saveBtn = document.getElementById(DOMStrings.saveBtn);
                saveBtn.addEventListener("click", function(event) {
                    baseView.renderLoading();
                    saveBtn.disabled = true;
                    var sizerSaveRequester = baseCtrl.createRequester(URLs.createSizer, formData);
                    var newPromise = sizerSaveRequester.ajaxRequest();
                    newPromise.then(function (result) {
                        if (result.status == "success") {
                            toastr.options = {
                                timeOut: 200,
                                positionClass: 'toast-top-right',
                                onHidden: function() {window.location.href=result.url}
                            };
                            toastr.success("创建选型成功");
                        } else if (result.status == "failure") {
                            toastr.options = {
                                timeOut: 200,
                                positionClass: 'toast-top-right'
                            };
                            toastr.error(result.errorCode);
                        }
                        baseView.removeLoading();
                        saveBtn.disabled = false;
                    })
                });
            });
        });
    };

    var clearFormInputError = function(event) {
        baseView.clearFormInputError(event.target);
    };

    var formValidation = function() {
        baseView.deleteErrorTip();
        if (!vldCtrl.validateFields()) {
            baseView.renderErrorTip();
            return false;
        }
        return true;
    };

    var ctrlAddWorkingCondition = function(option) {
        newWorkingOption = wkCondCtrl.addWkCond(option);
         wkViewCtrl.addWkTable(newWorkingOption);
    };

    var ctrlDeleteWorkingCondition = function(event) {
        var table = event.target.closest('.col-sm-4');
        var cond_length = wkCondCtrl.getWkCondInUse();
        if (cond_length <= 1) {
            toastr.error("无法删除，至少需要一组工况点");
            return;
        }
        wkViewCtrl.deleteWkTable(table);
        var id = parseInt(table.dataset.tableid);
        wkCondCtrl.deleteWkCond(id);
    };

    var ctrlAddWorkingPoint = function(event) {
        var addRow = event.target.closest('tr');
        var input = wkViewCtrl.getRowInput(addRow);
        wkViewCtrl.addWkPoint(input, addRow);
        wkViewCtrl.clearRowInput(addRow);
    };

    var ctrlDeleteWorkingPoint = function(event) {
        var pointLength = event.target.closest('table').querySelectorAll(".point").length;
        if (pointLength <= 1) {
            toastr.error("无法删除，每组工况至少需要一个工况点");
            return;
        }
        var row = event.target.closest('tr');
        wkViewCtrl.deleteWkPoint(row);
    };

    var initTables = function() {
        var data = [
            {inletPressure: "0.988", inletTemp: "40", inletReltHumi: "90"},
            {inletPressure: "0.988", inletTemp: "20", inletReltHumi: "70"},
            {inletPressure: "0.988", inletTemp: "0", inletReltHumi: "60"},
        ];
        data.forEach(function(option) {
            ctrlAddWorkingCondition(option);
        })
    };

    return {
        init: function() {
            setupEventListeners();
            initTables();
        }
    };
})(baseView, baseController, cardController, workingConditionController, workingConditionViewController, validateCtrl);

controller.init();