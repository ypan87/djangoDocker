/**
 * Created by yifan_pan on 2019/8/26.
 */
let strategies = {
	isNonEmpty: function(value, errorMsg) {
		if (value == '') {
			return errorMsg;
		}
	},
	isNotNumber: function(value, errorMsg) {
		if (typeof value != 'number') {
			return errorMsg;
		}
	},
	minLength: function(value, length, errorMsg) {
		if (value.length < length) {
			return errorMsg;
		}
	},
};

let Validator = function() {
	this.cache = [];
}

Validator.prototype.add = function(dom, rules) {
	let self = this;

	for (let i = 0, rule; rule = rules[i++];) {
		(function(rule) {
			let strategyAry = rule.strategy.split(':');
			let errorMsg = rule.errorMsg;

			self.cache.push(function() {
				let strategy = strategyAry.shift();
				strategyAry.unshift(dom.value);
				strategyAry.push(errorMsg);
				result = {
					dom: dom,
					msg: strategies[strategy].apply(dom, strategyAry),
				};
				return result;
			})
		})(rule)
	}

	Validator.prototype.start = function() {
		let results = [];
		for (let i = 0, validatorFunc; validatorFunc = this.cache[i++];) {
			let result = validatorFunc();
			if (result.msg) {
				results.push(result);
			}
		}
		return results;
	}
}
