/**
 * Created by yifan_pan on 19/4/9.
 */
var ctx = document.getElementById('firstChart').getContext('2d');
var ctx2 = document.getElementById('secondChart').getContext('2d');
var ctx3 = document.getElementById('threeChart').getContext('2d');


$('#selectButton').on('click', function() {
    var _self = $(this);
    $.ajax({
        cache: false,
        type: 'post',
        dataType:'json',
        url:"/turbo/selection/",
        data: $('#selectForm').serialize(),
        async: true,
        beforeSend:function(XMLHttpRequest){
            _self.val("提交中...");
            _self.attr("disabled","disabled");
            let graphCard = document.getElementById('graphCard');
            if (!graphCard.classList.contains('no-display')) {
                graphCard.classList.add('no-display');
            }
        },
        success: function(data) {
            let table = document.createElement('div');
            table.className = "row";
            table.innerHTML=[
                    '<div class="table-responsive col-12">',
                        '<table class="table table-bordered table-hover" style="text-align: center; max-width: 100%">',
                        '<thead class="thead-dark" style="max-width: 100%">',
                        '<tr>',
                            '<th scope="col">风机型号：GL1</th>',
                            '<th scope="col" colspan="3">40C/90%</th>',
                            '<th scope="col" colspan="3">20C/70%</th>',
                            '<th scope="col" colspan="3">0C/60%</th>',
                        '</tr>',
                        '</thead>',
                        '<tbody style="max-width: 100%">',
                        '<tr>',
                            '<th scope="row">进气压力</th>',
                            '<td colspan="3">0.988 bara</td>',
                            '<td colspan="3">0.988 bara</td>',
                            '<td colspan="3">0.988 bara</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">相对流量</th>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>轴功率</td>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>轴功率</td>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>轴功率</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">%</th>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">100%</th>',
                            '<td>0.6</td>',
                            '<td>4028.1</td>',
                            '<td>78.8</td>',
                            '<td>0.6</td>',
                            '<td>3576.8</td>',
                            '<td>68.8</td>',
                            '<td>0.6</td>',
                            '<td>3289.8</td>',
                            '<td>65.9</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">90%</th>',
                            '<td>0.6</td>',
                            '<td>3625.3</td>',
                            '<td>67.7</td>',
                            '<td>0.6</td>',
                            '<td>3219.1</td>',
                            '<td>62.7</td>',
                            '<td>0.6</td>',
                            '<td>2960.8</td>',
                            '<td>59.8</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">80%</th>',
                            '<td>0.6</td>',
                            '<td>3222.5</td>',
                            '<td>60.3</td>',
                            '<td>0.6</td>',
                            '<td>2861.4</td>',
                            '<td>56.2</td>',
                            '<td>0.6</td>',
                            '<td>2631.8</td>',
                            '<td>53.8</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">70%</th>',
                            '<td>0.6</td>',
                            '<td>2819.7</td>',
                            '<td>53.8</td>',
                            '<td>0.6</td>',
                            '<td>2503.7</td>',
                            '<td>50.1</td>',
                            '<td>0.6</td>',
                            '<td>2302.9</td>',
                            '<td>48.1</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">60%</th>',
                            '<td>0.6</td>',
                            '<td>2416.9</td>',
                            '<td>47.3</td>',
                            '<td>0.6</td>',
                            '<td>2146.1</td>',
                            '<td>44.1</td>',
                            '<td>0.6</td>',
                            '<td>1973.9</td>',
                            '<td>42.5</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">45%</th>',
                            '<td>0.6</td>',
                            '<td>1812.6</td>',
                            '<td>37.7</td>',
                            '<td>0.6</td>',
                            '<td>1609.5</td>',
                            '<td>35.5</td>',
                            '<td>0.6</td>',
                            '<td>1480.4</td>',
                            '<td>34.9</td>',
                        '</tr>',
                        '</tbody>',
                    '</table>',
                    '</div>',
                    '<div class="table-responsive col-12">',
                        '<table class="table table-bordered table-hover" style="text-align: center; max-width: 100%">',
                        '<thead class="thead-dark" style="max-width: 100%">',
                        '<tr>',
                            '<th scope="col">风机型号：GL1</th>',
                            '<th scope="col" colspan="3">40C/90%</th>',
                            '<th scope="col" colspan="3">20C/70%</th>',
                            '<th scope="col" colspan="3">0C/60%</th>',
                        '</tr>',
                        '</thead>',
                        '<tbody style="max-width: 100%">',
                        '<tr>',
                            '<th scope="row">进气压力</th>',
                            '<td colspan="3">0.988 bara</td>',
                            '<td colspan="3">0.988 bara</td>',
                            '<td colspan="3">0.988 bara</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">相对流量</th>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>进线功率</td>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>进线功率</td>',
                            '<td>ΔP</td>',
                            '<td>流量</td>',
                            '<td>进线功率</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">%</th>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                            '<td>barG</td>',
                            '<td>m<sup>3</sup>/h</td>',
                            '<td>kW</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">100%</th>',
                            '<td>0.6</td>',
                            '<td>4028.1</td>',
                            '<td>78.8</td>',
                            '<td>0.6</td>',
                            '<td>3576.8</td>',
                            '<td>68.8</td>',
                            '<td>0.6</td>',
                            '<td>3289.8</td>',
                            '<td>65.9</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">90%</th>',
                            '<td>0.6</td>',
                            '<td>3625.3</td>',
                            '<td>67.7</td>',
                            '<td>0.6</td>',
                            '<td>3219.1</td>',
                            '<td>62.7</td>',
                            '<td>0.6</td>',
                            '<td>2960.8</td>',
                            '<td>59.8</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">80%</th>',
                            '<td>0.6</td>',
                            '<td>3222.5</td>',
                            '<td>60.3</td>',
                            '<td>0.6</td>',
                            '<td>2861.4</td>',
                            '<td>56.2</td>',
                            '<td>0.6</td>',
                            '<td>2631.8</td>',
                            '<td>53.8</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">70%</th>',
                            '<td>0.6</td>',
                            '<td>2819.7</td>',
                            '<td>53.8</td>',
                            '<td>0.6</td>',
                            '<td>2503.7</td>',
                            '<td>50.1</td>',
                            '<td>0.6</td>',
                            '<td>2302.9</td>',
                            '<td>48.1</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">60%</th>',
                            '<td>0.6</td>',
                            '<td>2416.9</td>',
                            '<td>47.3</td>',
                            '<td>0.6</td>',
                            '<td>2146.1</td>',
                            '<td>44.1</td>',
                            '<td>0.6</td>',
                            '<td>1973.9</td>',
                            '<td>42.5</td>',
                        '</tr>',
                        '<tr>',
                            '<th scope="row">45%</th>',
                            '<td>0.6</td>',
                            '<td>1812.6</td>',
                            '<td>37.7</td>',
                            '<td>0.6</td>',
                            '<td>1609.5</td>',
                            '<td>35.5</td>',
                            '<td>0.6</td>',
                            '<td>1480.4</td>',
                            '<td>34.9</td>',
                        '</tr>',
                        '</tbody>',
                    '</table>',
                    '</div>'
            ].join('');
            // let graphCardBody = document.getElementById('graphCardBody');
            // graphCardBody.insertBefore(table, graphCardBody.firstChild);
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
            generateGraph(data.condOne, conditionColors, conditionLabels, ctx);
            generateGraph(data.condTwo, conditionColors, conditionLabels, ctx2);
            generateGraph(data.condThree, conditionColors, conditionLabels, ctx3);
        },
        complete: function(XMLHttpRequest){
            _self.val("提交");
            _self.removeAttr("disabled");
            let graphCard = document.getElementById('graphCard');
            if (graphCard.classList.contains('no-display')) {
                graphCard.classList.remove('no-display');
            }

            // 页面滑动至结果处
            var speed = 1600;
            var H = $("#graphCard").offset().top;
            $('body,html').animate({ scrollTop: H }, speed);
        }
    });
});

function generateGraph(data, conditionColors, conditionLabels, elem) {
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
    let newChart = new Chart(elem, {
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
                text: '流量压力曲线及轴功率，工况I：'
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