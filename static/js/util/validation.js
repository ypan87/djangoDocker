/**
 * Created by yifan_pan on 2019/10/14.
 */
export default class Validation {
    constructor() {
        this.cache = [];
    }

    add(dom, rules) {
        let self = this;
        for (var i = 0; i < rules.length; i++) {
            (function(rule) {
                self.cache.push(function() {
                    let strategyAry = rule.strategy.split(':');
                    let errorMsg = rule.errorMsg;
                    let strategy = strategyAry.shift();
                    strategyAry.unshift(dom.value);
                    strategyAry.push(errorMsg);
                    // 返回dom元素以及验证函数返回的信息
                    return strategies[strategy].apply(dom, strategyAry);
                })
            })(rules[i]);
        }
    }

    start() {
		let results = [];
		for (let i = 0, validatorFunc; validatorFunc = this.cache[i++];) {
			let result = validatorFunc();
			if (result.msg) {
				results.push(result);
			}
		}
		return results;
	}

	remove(dom) {
		let self = this;
		for (var i = 0; i < self.cache.length; i++) {
			let elem = self.cache[i]();
			if (elem.dom != dom) continue;
			self.cache.splice(i, 1);
		}
	}

}

let strategies = {
	isNonEmpty: function(value, errorMsg) {
		if (value == '') {
			return {
                dom: this,
                msg: errorMsg
            };
		}
		return {
			dom: this
		}
	},
	isNumber: function(value, errorMsg) {
		if (!/(^(-?\d+)(\.\d+)?$)/.test(value)) {
			return {
                dom: this,
                msg: errorMsg
            };
		}
		return {
			dom: this
		}
	},
	minLength: function(value, length, errorMsg) {
		if (value.length < length) {
			return {
                dom: this,
                msg: errorMsg
            };
		}
		return {
			dom: this
		}
	},
	maxLength: function(value, length, errorMsg) {
		if (value.length > length) {
			return {
                dom: this,
                msg: errorMsg
            };
		}
		return {
			dom: this
		}
	},
	minValue: function(value, minValue, errorMsg) {
		if (value < parseInt(minValue)) {
            return {
                dom: this,
                msg: errorMsg
            };
        }
        return {
        	dom: this
        }
	},
	maxValue: function(value, maxValue, errorMsg) {
		if (value > parseInt(maxValue)) {
			return {
				dom: this,
				msg: errorMsg
			}
		}
		return {
			dom: this
		}
	},
	email: function(value, errorMsg) {
		var emailRegExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
		if (!emailRegExp.test(value)) {
			return {
				dom: this,
				msg: errorMsg
			}
		}
		return {
			dom: this
		}
	},
	password: function(value, errorMsg) {
		var passwordRegExp = /^[a-zA-Z0-9_-]{6,20}$/;
		if (!passwordRegExp.test(value)) {
			return {
				dom: this,
				msg: errorMsg
			}
		}
		return {
			dom: this
		}
	}
};
