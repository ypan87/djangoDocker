/**
 * Created by yifan_pan on 19/4/9.
 */
let ctx = document.getElementById('firstChart');
let ctx2 = document.getElementById('secondChart');
let ctx3 = document.getElementById('threeChart');
let myChart1, myChart2, myChart3;
let btn = document.getElementById("selectButton");

let numberOnlyInput = [
    "projectAltitude", "projectInletPressure", "projectFrequency", "projectMachNums", "machVolt",
    "securityCoeff", "eiRating", "ambTemp", "ratedFlow", "ratedPressure", "ratedTemp",
    "rpPressure", "rpInletLoss", "rpOutLetLoss", "rpOutletPressure", "rpInletTemp",
    "dp1Pressure", "dp1InletTemp", "dp1p1Pressure", "dp1p2Pressure", "dp1p3Pressure", "dp1p4Pressure",
    "dp1p5Pressure", "dp1p6Pressure", "dp2Pressure", "dp2InletTemp", "dp2p1Pressure", "dp2p2Pressure",
    "dp2p3Pressure", "dp2p4Pressure", "dp2p5Pressure", "dp2p6Pressure", "dp3Pressure", "dp3InletTemp",
    "dp3p1Pressure", "dp3p2Pressure", "dp3p3Pressure", "dp3p4Pressure", "dp3p5Pressure", "dp3p6Pressure",
];

let numberRangeInput = [
    "ratedHumidity", "rpInletHumidity", "dp1InletHumidity", "dp1p1flow", "dp1p2flow",
    "dp1p3flow", "dp1p4flow", "dp1p5flow", "dp1p6flow", "dp2InletHumidity",
    "dp2p1flow", "dp2p2flow", "dp2p3flow", "dp2p4flow", "dp2p5flow", "dp2p6flow",
    "dp3InletHumidity", "dp3p1flow", "dp3p2flow", "dp3p3flow", "dp3p4flow",
    "dp3p5flow", "dp3p6flow",
];

function numberOnlyValidate() {
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.innerHTML = "";
    if (isNaN(this.value)) {
        this.nextElementSibling.className = "error";
        this.nextElementSibling.innerHTML = "请输入数字";
    } else if (!isNaN(this.value)) {
        if (this.value < 0) {
            this.nextElementSibling.className = "error";
            this.nextElementSibling.innerHTML = "输入值应该大于0";
        } else {
            this.nextElementSibling.classList.add("hidden");
            this.nextElementSibling.innerHTML = "";
        }
    }
}

function numberRangeValidate() {
    this.nextElementSibling.classList.add("hidden");
    this.nextElementSibling.innerHTML = "";
    if (isNaN(this.value)) {
        this.nextElementSibling.className = "error";
        this.nextElementSibling.innerHTML = "请输入数字";
    } else if (!isNaN(this.value)) {
        if (this.value < 0 || this.value > 100) {
            this.nextElementSibling.className = "error";
            this.nextElementSibling.innerHTML = "输入值应该大于0，小于100";
        } else {
            this.nextElementSibling.classList.add("hidden");
            this.nextElementSibling.innerHTML = "";
        }
    }
}

for (let id of numberOnlyInput) {
    let elem = document.getElementById(id);
    elem.addEventListener("keyup", numberOnlyValidate)
}

for (let id of numberRangeInput) {
    let elem = document.getElementById(id);
    elem.addEventListener("keyup", numberRangeValidate)
}

// 前端数据验证
$('#selectButton').on('click', function() {
    let _self = $(this);
    $.ajax({
        cache: false,
        type: 'post',
        dataType:'json',
        url:"/turbo/selection/",
        data: $('#selectForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){
            _self.addClass("disabled");
            _self.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>提交中');
            let graphCard = document.getElementById('graphCard');
            if (!graphCard.classList.contains('no-display')) {
                graphCard.classList.add('no-display');
            }

        },
        success: function(data) {
            if (data.status == "error") {
                for (let key in data) {
                    if (key == "status") {
                        continue;
                    }
                    let elem = document.getElementById(key);
                    elem.nextElementSibling.className = "error";
                    elem.nextElementSibling.innerHTML = data[key];
                }
                return false;
            }
            let table = generateTableHtml(data);
            let tableContent = document.getElementById("tableContent");
            for (let i=0; i < tableContent.childNodes.length; i++) {
                tableContent.childNodes[i].remove();
            }
            tableContent.appendChild(table);

            // 颜色数组
            let conditionColors = [
                'rgb(25,202,173)',
                'rgb(140,199,181)',
                'rgb(160,238,225)',
                'rgb(190,231,233)',
                'rgb(190,237,199)',
                'rgb(214,231,183)',
                'rgb(209,186,116)',
                'rgb(230,206,172)',
                'rgb(236,173,158)',
                'rgb(244,96,108)',
                'rgb(205,164,158)',
            ];

            // label数组
            let conditionLabels = [
                "流量压升曲线一",
                "流量压升曲线二",
                "流量压升曲线三",
                "流量压升曲线四",
                "流量压升曲线五",
                "流量压升曲线六",
                "流量压升曲线七",
                "流量压升曲线八",
                "流量压升曲线九",
                "流量压升曲线十",
                "流量压升曲线十一",
            ];

            // 产生图标
            myChart1 = generateGraph(data.condOne, conditionColors, conditionLabels, ctx, myChart1, "工况I");
            myChart2 = generateGraph(data.condTwo, conditionColors, conditionLabels, ctx2, myChart2, "工况II");
            myChart3 = generateGraph(data.condThree, conditionColors, conditionLabels, ctx3, myChart3, "工况III");

            let graphCard = document.getElementById('graphCard');
            if (graphCard.classList.contains('no-display')) {
                graphCard.classList.remove('no-display');
            }

            // 页面滑动至结果处
            var speed = 1600;
            var H = $("#graphCard").offset().top;
            $('body,html').animate({ scrollTop: H }, speed);
        },
        complete: function(XMLHttpRequest){
            _self.removeClass("disabled");
            _self.html('提交');
        }
    });
});

// 生成表格html内容
function generateTableHtml(data) {
    let table = document.createElement('div');
    tableData = data.tableData;
    table.className = "row";
    table.innerHTML=
        '<div class="table-responsive col-12">'+
        '<table class="table table-bordered table-hover" style="text-align: center; max-width: 100%">'+
        '<thead class="thead-dark" style="max-width: 100%">'+
        '<tr>'+
        '<th scope="col">风机型号：'+ tableData.turbo + '</th>'+
        '<th scope="col" colspan="3">' + tableData.condition1.temp + 'C/' + tableData.condition1.humidity +'%</th>'+
        '<th scope="col" colspan="3">' + tableData.condition2.temp + 'C/' + tableData.condition2.humidity +'%</th>'+
        '<th scope="col" colspan="3">' + tableData.condition3.temp + 'C/' + tableData.condition3.humidity +'%</th>'+
        '</tr>'+
        '</thead>'+
        '<tbody style="max-width: 100%">'+
        '<tr>'+
        '<th scope="row">进气压力</th>'+
        '<td colspan="3">' + tableData.condition1.baraPressure + ' bara</td>'+
        '<td colspan="3">' + tableData.condition2.baraPressure + ' bara</td>'+
        '<td colspan="3">' + tableData.condition3.baraPressure + ' bara</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">相对流量</th>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>轴功率</td>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>轴功率</td>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>轴功率</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">%</th>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[0].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[0].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].shaftPower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[1].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[1].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].shaftPower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[2].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[2].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].shaftPower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[3].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[3].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].shaftPower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[4].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[4].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].shaftPower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[5].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[5].shaftPower + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].shaftPower + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].shaftPower + '</td>'+
        '</tr>'+
        '</tbody>'+
        '</table>'+
        '</div>'+
        '<div class="table-responsive col-12">'+
        '<table class="table table-bordered table-hover" style="text-align: center; max-width: 100%">'+
        '<thead class="thead-dark" style="max-width: 100%">'+
        '<tr>'+
        '<th scope="col">风机型号：'+ tableData.turbo + '</th>'+
        '<th scope="col" colspan="3">' + tableData.condition1.temp + 'C/' + tableData.condition1.humidity +'%</th>'+
        '<th scope="col" colspan="3">' + tableData.condition2.temp + 'C/' + tableData.condition2.humidity +'%</th>'+
        '<th scope="col" colspan="3">' + tableData.condition3.temp + 'C/' + tableData.condition3.humidity +'%</th>'+
        '</tr>'+
        '</thead>'+
        '<tbody style="max-width: 100%">'+
        '<tr>'+
        '<th scope="row">进气压力</th>'+
        '<td colspan="3">' + tableData.condition1.baraPressure + ' bara</td>'+
        '<td colspan="3">' + tableData.condition2.baraPressure + ' bara</td>'+
        '<td colspan="3">' + tableData.condition3.baraPressure + ' bara</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">相对流量</th>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>进线功率</td>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>进线功率</td>'+
        '<td>ΔP</td>'+
        '<td>流量</td>'+
        '<td>进线功率</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">%</th>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '<td>barG</td>'+
        '<td>m<sup>3</sup>/h</td>'+
        '<td>kW</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[0].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[0].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[0].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[0].wirePower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[1].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[1].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[1].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[1].wirePower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[2].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[2].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[2].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[2].wirePower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[3].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[3].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[3].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[3].wirePower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[4].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[4].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[4].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[4].wirePower + '</td>'+
        '</tr>'+
        '<tr>'+
        '<th scope="row">'+ tableData.condition1.dataSet[5].relativeFlow +'%</th>'+
        '<td>' + tableData.condition1.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition1.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition1.dataSet[5].wirePower + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition2.dataSet[5].wirePower + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].outletPress + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].flowAmb + '</td>'+
        '<td>' + tableData.condition3.dataSet[5].wirePower + '</td>'+
        '</tr>'+
        '</tbody>'+
        '</table>'+
        '</div>';
    return table;
}

// 生成图表
function generateGraph(data, conditionColors, conditionLabels, elem, chart, title) {
    if (chart) {
        chart.destroy();
    }

    let datasets = [];
    let condData = data[0];
    let powerData = data[1];
    let designData = data[2];
    for (let i = 0; i < 11; i++) {
        let singleData = generateData(condData[i], "condition", conditionLabels[i], conditionColors[i]);
        datasets.push(singleData);
    }

    let powerGraphData = generateData(powerData, "power", "流量轴功率曲线", "rgb(0,90,171)");
    datasets.push(powerGraphData);

    let designGraphData = generateData(designData, "design", "设计点流量压升", "black");
    datasets.push(designGraphData);

    // 创建图表
    return new Chart(elem.getContext("2d"), {
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
                text: '流量压力曲线及轴功率' + title + '：'
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
}

// 获取图表数据
function generateData(dataArray, category, label, color) {
    dataPoints = [];
    for (let point of dataArray) {
        let dataPoint = {
            x: point[0],
            y: point[1]
        };
        dataPoints.push(dataPoint)
    }
    let chartData = {
        label: label,
        data: dataPoints,
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        showLine: category == "design" ? false : true,
        fill: false,
        yAxisID: category == "power" ? 'y-axis-2' : "y-axis-1",
        pointRadius: 2
    };
    return chartData
}