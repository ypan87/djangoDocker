/**
 * Created by yifan_pan on 2019/10/15.
 */

export class Conditions {
    constructor() {
        this.wkCondsAll = [];
        this.wkCondsInUse = [];
        this.ids = [];
    }

    addWkCond(option) {
        var id;
        // 如果还有id可以使用，则找到对应的Condition然后返回
        if (this.ids.length > 0) {
            id = this.ids.shift();
        } else {
            // 如果没有id可以使用，则新建新的Condition返回
            var condsLength = this.wkCondsAll.length;
            if (condsLength == 0) {
                id = 0;
            } else {
                id = this.wkCondsAll[condsLength - 1] + 1;
            }
            this.wkCondsAll.push(id);
        }
        this.wkCondsInUse.push(id);

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
    }

    deleteWkCond(id) {
        this.ids.push(id);
        var index = findIdIndexInAry(this.wkCondsInUse, id);
        this.wkCondsInUse.splice(index, 1);
    }

    getWkCondInUse() {
        return this.wkCondsInUse.length;
    }
}

var findIdIndexInAry = function(ary, id) {
    return ary.findIndex(function(el) {
        return el == id;
    });
};
