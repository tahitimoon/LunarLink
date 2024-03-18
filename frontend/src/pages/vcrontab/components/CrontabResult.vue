<template>
    <div class="popup-result">
        <p class="title">最近5次运行时间</p>
        <ul class="popup-result-scroll">
            <template v-if="isShow">
                <li v-for="item in resultList" :key="item">{{ item }}</li>
            </template>
            <li v-else>计算结果中...</li>
        </ul>
    </div>
</template>

<script>
export default {
    name: "CrontabResult",
    data() {
        return {
            dateArr: [],
            resultList: [],
            isShow: false
        };
    },
    props: {
        ex: {
            type: String,
            default: ""
        }
    },
    methods: {
        // 表达式值变化时，开始去计算结果
        expressionChange() {
            this.isShow = false;
            let ruleArr = this.$options.propsData.ex.split(" ");
            let nums = 0;
            let resultArr = [];
            let nTime = new Date();
            let nYear = nTime.getFullYear();
            let nMouth = nTime.getMonth() + 1;
            let nDay = nTime.getDate();
            let nHour = nTime.getHours();
            let nMin = nTime.getMinutes();
            let nSecond = nTime.getSeconds();

            this.getMinArr(ruleArr[0]);
            this.getHourArr(ruleArr[1]);
            this.getDayArr(ruleArr[2]);
            this.getMouthArr(ruleArr[3]);
            this.getWeekArr(ruleArr[4]);

            let mDate = this.dateArr[0];
            let hDate = this.dateArr[1];
            let DDate = this.dateArr[2];
            let MDate = this.dateArr[3];
            let WDate = this.dateArr[4];
            let YDate = this.getOrderArr(nYear, nYear + 100);

            let mIdx = this.getIndex(mDate, nMin);
            let hIdx = this.getIndex(hDate, nHour);
            let DIdx = this.getIndex(DDate, nDay);
            let MIdx = this.getIndex(MDate, nMouth);
            let YIdx = this.getIndex(YDate, nYear);

            const resetMin = () => {
                mIdx = 0;
                nMin = mDate[mIdx];
                nSecond = 0;
            };

            const resetHour = () => {
                hIdx = 0;
                nHour = hDate[hIdx];
                resetMin();
            };

            const resetDay = () => {
                DIdx = 0;
                nDay = DDate[DIdx];
                resetHour();
            };

            const resetMouth = () => {
                MIdx = 0;
                nMouth = MDate[MIdx];
                resetDay();
            };

            if (nMouth !== MDate[MIdx]) {
                resetDay();
            }

            if (nDay !== DDate[DIdx]) {
                resetHour();
            }

            if (nHour !== hDate[hIdx]) {
                resetMin();
            }

            if (nMin !== mDate[mIdx]) {
                nSecond = 0;
            }

            goYear: for (let Yi = YIdx; Yi < YDate.length; Yi++) {
                let YY = YDate[Yi];
                if (nMouth > MDate[MDate.length - 1]) {
                    resetMouth();
                    continue;
                }

                goMouth: for (let Mi = MIdx; Mi < MDate.length; Mi++) {
                    let MM = MDate[Mi];
                    MM = MM < 10 ? "0" + MM : MM;
                    if (nDay > DDate[DDate.length - 1]) {
                        resetDay();
                        if (Mi == MDate.length - 1) {
                            resetMouth();
                            continue goYear;
                        }
                        continue;
                    }

                    goDay: for (let Di = DIdx; Di < DDate.length; Di++) {
                        let DD = DDate[Di];
                        let thisDD = DD < 10 ? "0" + DD : DD;
                        if (nHour > hDate[hDate.length - 1]) {
                            resetHour();
                            if (Di == DDate.length - 1) {
                                resetDay();
                                if (Mi == MDate.length - 1) {
                                    resetMouth();
                                    continue goYear;
                                }
                                continue goMouth;
                            }
                            continue;
                        }

                        goHour: for (let Hi = hIdx; Hi < hDate.length; Hi++) {
                            let HH = hDate[Hi];
                            HH = HH < 10 ? "0" + HH : HH;
                            if (nMin > mDate[mDate.length - 1]) {
                                resetMin();
                                if (Hi == hDate.length - 1) {
                                    resetHour();
                                    if (Di == DDate.length - 1) {
                                        resetDay();
                                        if (Mi == MDate.length - 1) {
                                            resetMouth();
                                            continue goYear;
                                        }
                                        continue goMouth;
                                    }
                                    continue goDay;
                                }
                                continue;
                            }

                            goMin: for (
                                let Mi = mIdx;
                                Mi < mDate.length;
                                Mi++
                            ) {
                                let mm = mDate[Mi];
                                mm = mm < 10 ? "0" + mm : mm;
                                if (nSecond > 59) {
                                    nSecond = 0;
                                    if (Mi == mDate.length - 1) {
                                        resetMin();
                                        if (Hi == hDate.length - 1) {
                                            resetHour();
                                            if (Di == DDate.length - 1) {
                                                resetDay();
                                                if (Mi == MDate.length - 1) {
                                                    resetMouth();
                                                    continue goYear;
                                                }
                                                continue goMouth;
                                            }
                                            continue goDay;
                                        }
                                        continue goHour;
                                    }
                                    continue;
                                }

                                let result =
                                    YY +
                                    "-" +
                                    MM +
                                    "-" +
                                    thisDD +
                                    " " +
                                    HH +
                                    ":" +
                                    mm +
                                    ":" +
                                    (nSecond < 10 ? "0" + nSecond : nSecond);
                                if (this.checkWeek(result, WDate) !== true) {
                                    continue;
                                }

                                resultArr.push(result);
                                nums++;
                                if (nums >= 5) {
                                    break goYear;
                                }
                                nSecond = 0;
                            }
                            resetMin();
                        }
                        resetHour();
                    }
                    resetDay();
                }
                resetMouth();
            }

            this.resultList = resultArr;
            this.isShow = true;
        },
        getMinArr(rule) {
            this.dateArr[0] = this.getOrderArr(0, 59, rule);
        },
        getHourArr(rule) {
            this.dateArr[1] = this.getOrderArr(0, 23, rule);
        },
        getDayArr(rule) {
            this.dateArr[2] = this.getOrderArr(1, 31, rule);
        },
        getMouthArr(rule) {
            this.dateArr[3] = this.getOrderArr(1, 12, rule);
        },
        getWeekArr(rule) {
            if (rule === "0") rule = "7";
            this.dateArr[4] = this.getOrderArr(1, 7, rule);
        },
        getOrderArr(start, end, rule) {
            let arr = [];
            if (rule === undefined || rule === "*" || rule === "?") {
                for (let i = start; i <= end; i++) {
                    arr.push(i);
                }
            } else if (rule.indexOf("-") !== -1) {
                let ruleArr = rule.split("-");
                for (
                    let i = parseInt(ruleArr[0]);
                    i <= parseInt(ruleArr[1]);
                    i++
                ) {
                    arr.push(i);
                }
            } else if (rule.indexOf(",") !== -1) {
                let ruleArr = rule.split(",");
                for (let i = 0; i < ruleArr.length; i++) {
                    arr.push(parseInt(ruleArr[i]));
                }
            } else if (rule.indexOf("/") !== -1) {
                let ruleArr = rule.split("/");
                let step = parseInt(ruleArr[1]);
                for (
                    let i = parseInt(ruleArr[0] === "*" ? start : ruleArr[0]);
                    i <= end;
                    i += step
                ) {
                    arr.push(i);
                }
            } else {
                arr.push(parseInt(rule));
            }
            return arr;
        },
        getIndex(arr, val) {
            for (let i = 0; i < arr.length; i++) {
                if (arr[i] >= val) {
                    return i;
                }
            }
            return 0;
        },
        checkWeek(dateString, weekArr) {
            let date = new Date(dateString);
            let day = date.getDay();
            day = day === 0 ? 7 : day;
            return weekArr.includes(day);
        }
    },
    watch: {
        ex: function(newVal, oldVal) {
            if (newVal !== oldVal) {
                this.expressionChange();
            }
        }
    },
    mounted() {
        this.expressionChange();
    }
};
</script>
