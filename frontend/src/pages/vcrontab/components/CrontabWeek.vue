<template>
    <el-form size="small">
        <el-form-item>
            <el-radio v-model="radioValue" :label="1">
                周，允许的通配符[, - * /]
            </el-radio>
        </el-form-item>

        <el-form-item>
            <el-radio v-model="radioValue" :label="3">
                周期从星期
                <el-input-number v-model="cycle01" :min="1" :max="7" /> -
                <el-input-number v-model="cycle02" :min="1" :max="7" />
            </el-radio>
        </el-form-item>

        <el-form-item>
            <el-radio v-model="radioValue" :label="6">
                指定
                <el-select
                    clearable
                    v-model="checkboxList"
                    placeholder="可多选"
                    multiple
                    style="width: 100%"
                >
                    <el-option
                        v-for="(item, index) of weekList"
                        :key="index"
                        :value="index + 1"
                        >{{ item }}</el-option
                    >
                </el-select>
            </el-radio>
        </el-form-item>
    </el-form>
</template>

<script>
export default {
    data() {
        return {
            radioValue: 2,
            weekday: 1,
            cycle01: 1,
            cycle02: 2,
            average01: 1,
            average02: 1,
            checkboxList: [],
            weekList: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            checkNum: this.$options.propsData.check
        };
    },
    name: "CrontabWeek",
    props: ["check", "cron"],
    methods: {
        // 单选按钮值变化时
        radioChange() {
            if (this.radioValue === 1) {
                this.$emit("update", "week", "*");
                this.$emit("update", "year", "*");
            } else {
                if (this.cron.mouth === "*") {
                    this.$emit("update", "mouth", "*", "week");
                }
                if (this.cron.day === "*") {
                    this.$emit("update", "day", "*", "week");
                }
                if (this.cron.hour === "*") {
                    this.$emit("update", "hour", "0", "week");
                }
                if (this.cron.min === "*") {
                    this.$emit("update", "min", "0", "week");
                }
                if (this.cron.second === "*") {
                    this.$emit("update", "second", "0", "week");
                }
            }
            switch (this.radioValue) {
                case 3:
                    this.$emit(
                        "update",
                        "week",
                        this.cycle01 + "-" + this.cycle02
                    );
                    break;
                case 6:
                    this.$emit("update", "week", this.checkboxString);
                    break;
            }
        },
        // 根据互斥事件，更改radio的值

        // 周期两个值变化时
        cycleChange() {
            if (this.radioValue == "3") {
                this.$emit("update", "week", this.cycleTotal);
            }
        },
        // checkbox值变化时
        checkboxChange() {
            if (this.radioValue == "6") {
                this.$emit("update", "week", this.checkboxString);
            }
        }
    },
    watch: {
        radioValue: "radioChange",
        cycleTotal: "cycleChange",
        checkboxString: "checkboxChange"
    },
    computed: {
        // 计算两个周期值
        cycleTotal: function() {
            this.cycle01 = this.checkNum(this.cycle01, 1, 7);
            this.cycle02 = this.checkNum(this.cycle02, 1, 7);
            return this.cycle01 + "-" + this.cycle02;
        },
        // 计算勾选的checkbox值合集
        checkboxString: function() {
            let str = this.checkboxList.join();
            return str == "" ? "*" : str;
        }
    }
};
</script>
