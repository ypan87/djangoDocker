// 表单的收放
let form = document.querySelector('#turboForm');
form.addEventListener('click', function(event) {
	let target = event.target;

	// 点击cardHeader并且不在button区域时，我们可以进行css动画
	let cardHeader = null;
	if (target.classList.contains('card-header') ) {
		cardHeader = target;
	} else if (target.closest('.card-header') && target.tagName != "BUTTON") {
		cardHeader = target.closest('.card-header');
	} else {
		return false;
	}

	// css动画
	let cardBody = cardHeader.nextElementSibling;
	let icon = cardHeader.querySelector('span');
	cardBody.classList.toggle('card-body-collapsed');
	cardHeader.classList.toggle('card-header-active');
	icon.classList.toggle('icon-rotate');
});

// 添加验证规则
let validataFunc = function() {
	let validator = new Validator();

	validator.add(form.projectName, [{
		strategy: 'isNonEmpty',
		errorMsg: '项目名不能为空'
	}]);

	return validator.start();
};

// 显示错误信息
let displayError = function(errorMsg) {
	let inputError = this.parentElement.getElementsByClassName('input-error')[0];
	inputError.innerHTML = errorMsg;
	if (inputError.classList.contains('hidden')) {
		inputError.classList.remove('hidden');
	}
};

// // 清除错误信息
// let clearError = function() {
// 	let inputError = this.parentElement.getElementsByClassName('input-error')[0];
// 	if (inputError) {
// 		inputError.innerHTML = '';
// 		if (!inputError.classList.contains('hidden')) {
// 			inputError.classList.add('hidden');
// 		}
// 	}
// }

// // 输入数据后错误信息消失
// let inputs = document.querySelectorAll('input');
// for (let i = 0, input; input = inputs[i++];) {
// 	input.addEventListener('keyup', function() {
// 		clearError.call(this);
// 	});
// }

// 表单提交
form.onsubmit = function() {
	let results = validataFunc();
	let hasNoError = true;
	for (let i = 0, result; result = results[i++];) {
		if (result.msg) {
			displayError.call(result.dom, result.msg);
		}
	}
};

// 修改语言
let elemLangChange = function(language) {
	let name = this.name;
	if (translation[language][name]) {
		this.innerHTML = translation[language][name];
	}
};

let elemsLangChange = function(language) {
	let changes = document.querySelectorAll('[data-translation]');
	for (let i = 0, div; div = changes[i++];) {
		elemLangChange.call(div, language);
	}
};

let loadingDisplay = function() {
	let loading = document.querySelector('.wrapper');
	if (loading.classList.contains("hidden")) {
		loading.classList.remove("hidden");
	}
};

let loadingClear = function() {
	let loading = document.querySelector('.wrapper');
	if (!loading.classList.contains("hidden")) {
		loading.classList.add("hidden");
	}
};

let langSelect = document.querySelector('#lang-select');
langSelect.addEventListener('change', function() {
	// 展示loading页面
	loadingDisplay();
	// 文字变化
	let index = this.selectedIndex;
	let value = this.options[index].value;
	elemsLangChange(value);
	// 隐藏loading页面
	loadingClear();
});

// 修改单位

// 工况组件
// 工况组件对象池
let conditionTableFactory = (function(){
	let tables = [];

	return {
		create: function(pressure, temp, humi,) {
			if (tables.length == 0) {
				let div = document.createElement("div");
				div.innerHTML = `
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
                                        <input type="text" class="form-control" value=${pressure || ''}>
                                    </td>
                                </tr>
                                <tr class="general">
                                    <th scope="row">进气温度</th>
                                    <td colspan="2">
                                        <input type="text" class="form-control" value=${temp || ''}>
                                    </td>
                                </tr>
                                <tr class="general">
                                    <th scope=row>进气相对湿度</th>
                                    <td colspan="2">
                                        <input type="text" class="form-control" value=${humi || ''}>
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="3"></td>
                                </tr>
                                <tr>
                                    <th scope="col">相对流量</th>
                                    <th scope="col">压力</th>
                                    <th scope="col">操作</th>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="100">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <!-- 可以修改td的对齐方式 -->
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="90">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="80">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="70">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="60">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr class="point">
                                    <td>
                                        <input type="text" class="form-control" value="45">
                                    </td>
                                    <td>
                                        <input type="text" class="form-control" value="0.6">
                                    </td>
                                    <td>
                                        <span class="row-del">
                                            <button type="button" class="btn btn-outline-danger">删除</button>
                                        </span>
                                    </td>
                                </tr>
                                <tr>
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
				`;
				div.classList = "col-sm-4";
				return div;
			} else {
				return tables.shift();
			}
		},
		recover: function(table) {
			return tables.push(table);
		}
	}
})();

// 初始化三个工况组件
let wrapper = document.querySelector('.condition-table-wrapper');
let conditionTableInitData = [["0.988","40", "90"], ["0.988", "20", "70"], ["0.988", "0", "60"]];
for (let i = 0; i < 3; i++) {
	let conditionTable = conditionTableFactory.create(conditionTableInitData[i][0],
		conditionTableInitData[i][1], conditionTableInitData[i][2],);
	wrapper.appendChild(conditionTable);
}

// 删除工况表
form.addEventListener('click', function(event) {
	let target = event.target;
	// 如果点击删除按钮的话，就直接删除所在的工况表
	if (target.parentElement.classList.contains('condition-table-close')) {
		// 找到最近的table并删除
		let table = target.closest('table');
		let wrapper = table.parentElement;
		conditionTableFactory.recover(wrapper);
		wrapper.remove();
	}
});

// 添加工况表
form.addEventListener('click', function(event) {
	let target = event.target;
	if (target.classList.contains('condition-table-add')) {
		let conditionTable = conditionTableFactory.create();
		wrapper.appendChild(conditionTable);
	}
});

// 删除行操作
form.addEventListener('click', function(event) {
	let target = event.target;
	// 如果是点击的删除按钮的话，就删除按钮所在的那一行
	if (target.parentElement.classList.contains('row-del')) {
		let row = target.closest('tr');
		row.remove();
	}
});

// 添加行操作
form.addEventListener('click', function(event) {
	let target = event.target;
	if (target.parentElement.classList.contains('row-add')) {
		// 数据验证（required, number)
		let row = target.closest('tr');
		// 克隆
		let cloneRow = row.cloneNode(true);
        cloneRow.classList = "point";
		// 修改内容
		let rowAdd = cloneRow.querySelector('.row-add');
		rowAdd.classList = "row-del";
		rowAdd.innerHTML = `<button type="button" class="btn btn-outline-danger">删除</button>`
		let tbody = target.closest('tbody');
		// 添加
		tbody.insertBefore(cloneRow, row);
		// 清除内容
		clearAllInputChildren(row);
	}
});

// 清除父元素下所有input子元素的内容
let clearAllInputChildren = function(parentElem) {
	let inputs = parentElem.querySelectorAll('input');
	for (i = 0; i < inputs.length; i++) {
		inputs[i].value = "";
	}
};

// 提交表格
form.addEventListener('submit', function(event) {
	event.preventDefault();
    // 获取普通的元素
    let elements = getElements(form);
    let elementsDict = getDictFromElements(elements);
    // 获取condition table 中的所有input元素
    let tables = document.querySelectorAll('.condition-table');
    // 将所有input组合成另一个键值对conditionTableArray
    elementsDict["conditionArray"] = getConditionTableArray(tables);

    let finalData = JSON.stringify(elementsDict);

    $.ajax({
        cache: false,
        type: 'POST',
        dataType:'json',
		contentType: "application/json; charset=UTF-8",
        url:"/turbo/selection/",
		headers:{ "X-CSRFtoken": getCookie('csrftoken')},
        data: finalData,
        async: true,
		beforeSend:function (xhr,settings) {
		},
        success: function(data) {
			console.log(data);
		}
    });
});

// 获取表格中的所有元素
let getElements = function(form) {
    let elements = [];
    let tagElements = form.getElementsByTagName('input');
    for (let i = 0; i < tagElements.length; i++) {
		if (tagElements[i].value) {
			elements.push(tagElements[i]);
		}
    }
    return elements;
};

// 将所有元素转换格式
let getDictFromElements = function(elements) {
    let a = {};
    for (let i = 0; i < elements.length; i++) {
        name = elements[i].name;
        value = elements[i].value;
        a[name] = value;
    }
    return a;
};

// 组合所有table中的input元素
let getConditionTableArray = function(tables) {
    let tablesArray = [];
    for (let i = 0; i < tables.length; i++) {
        let tableArray = [];
        let general = tables[i].querySelectorAll('tr.general');
        for (let j = 0; j < general.length; j++) {
            dict1 = {};
            let input = general[j].querySelector('input');
            switch(j) {
                case 0:
                    dict1 = {pressure: input.value};
                    break;
                case 1:
                    dict1 = {temp: input.value};
                    break;
                case 2:
                    dict1 = {humi: input.value};
                    break;
                default:
                    break;
            }
            tableArray.push(dict1);
        }

        let points = tables[i].querySelectorAll('tr.point');
        for (let j = 0; j < points.length; j++) {
            let input1 = points[j].querySelectorAll('input')[0];
            let input2 = points[j].querySelectorAll('input')[1];
            let dict1 = {
                flow: input1.value,
                pressure: input2.value
            };
            tableArray.push(dict1);
        }
        tablesArray.push(tableArray);
    }
    return tablesArray
};

function getCookie(name) {
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
}
