<template>
    <el-table
        highlight-current-row
        :cell-style="{ paddingTop: '4px', paddingBottom: '4px' }"
        stripe
        :height="height"
        :data="tableData"
        style="width: 100%;"
        @cell-mouse-enter="cellMouseEnter"
        @cell-mouse-leave="cellMouseLeave"
    >
        <el-table-column fixed label="实际返回值" width="300">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.actual"
                    placeholder="实际返回值"
                ></el-input>
            </template>
        </el-table-column>

        <el-table-column label="断言类型" width="180">
            <template v-slot="scope">
                <el-select v-model="scope.row.comparator">
                    <el-option
                        v-for="item in validateOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    ></el-option>
                </el-select>
            </template>
        </el-table-column>

        <el-table-column label="期望类型" width="120">
            <template v-slot="scope">
                <el-select v-model="scope.row.type">
                    <el-option
                        v-for="item in dataTypeOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    ></el-option>
                </el-select>
            </template>
        </el-table-column>

        <el-table-column label="期望返回值" width="300">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.expect"
                    placeholder="期望返回值"
                ></el-input>
            </template>
        </el-table-column>

        <el-table-column label="断言描述" width="300">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.desc"
                    placeholder="断言描述"
                ></el-input>
            </template>
        </el-table-column>

        <el-table-column>
            <template v-slot="scope">
                <el-row v-show="scope.row === currentRow">
                    <el-button
                        icon="el-icon-circle-plus-outline"
                        size="mini"
                        type="info"
                        title="增加变量"
                        @click="handleEdit"
                    ></el-button>
                    <el-button
                        icon="el-icon-document-copy"
                        size="mini"
                        type="info"
                        title="复制变量"
                        @click="handleCopy(scope.$index, scope.row)"
                    ></el-button>
                    <el-button
                        icon="el-icon-delete"
                        size="mini"
                        type="danger"
                        title="删除变量"
                        v-show="scope.$index !== 0"
                        @click="handleDelete(scope.$index)"
                    ></el-button>
                </el-row>
            </template>
        </el-table-column>
    </el-table>
</template>

<script>
import { isEqual } from "lodash";

export default {
    name: "Validate",
    data() {
        return {
            currentValidate: "",
            currentRow: "",
            originalTableData: [],
            tableData: [
                {
                    expect: "",
                    actual: "",
                    comparator: "equals",
                    type: 1,
                    desc: ""
                }
            ],
            dataTypeOptions: [
                {
                    label: "String",
                    value: 1
                },
                {
                    label: "Integer",
                    value: 2
                },
                {
                    label: "Float",
                    value: 3
                },
                {
                    label: "Boolean",
                    value: 4
                },
                {
                    label: "List",
                    value: 5
                },
                {
                    label: "Dict",
                    value: 6
                },
                {
                    label: "None",
                    value: 7
                }
            ],
            validateOptions: [
                {
                    value: "equals",
                    label: "等于"
                },
                {
                    value: "less_than",
                    label: "小于"
                },
                {
                    value: "less_than_or_equals",
                    label: "小于等于"
                },
                {
                    value: "greater_than",
                    label: "大于"
                },
                {
                    value: "greater_than_or_equals",
                    label: "大于等于"
                },
                {
                    value: "not_equals",
                    label: "不等于"
                },
                {
                    value: "string_equals",
                    label: "字符串相等"
                },
                {
                    value: "length_equals",
                    label: "长度相等"
                },
                {
                    value: "length_greater_than",
                    label: "长度大于"
                },
                {
                    value: "length_greater_than_or_equals",
                    label: "长度大于等于"
                },
                {
                    value: "length_less_than",
                    label: "长度小于"
                },
                {
                    value: "length_less_than_or_equals",
                    label: "长度小于等于"
                },
                {
                    value: "contains",
                    label: "包含"
                },
                {
                    value: "not_contains",
                    label: "不包含"
                },
                {
                    value: "contained_by",
                    label: "被包含"
                },
                {
                    value: "list_any_item_contains",
                    label: "列表任意元素包含"
                },
                {
                    value: "list_all_item_contains",
                    label: "列表所有元素包含"
                },
                {
                    value: "type_match",
                    label: "类型匹配"
                },
                {
                    value: "regex_match",
                    label: "正则匹配"
                },
                {
                    value: "startswith",
                    label: "以...开头"
                },
                {
                    value: "endswith",
                    label: "以...结尾"
                }
            ]
        };
    },
    props: {
        save: Boolean,
        validate: {
            required: false
        }
    },
    computed: {
        height() {
            return window.screen.height - 440;
        }
    },
    watch: {
        save() {
            this.$emit("validate", this.parseValidate(), this.tableData);
        },
        tableData: {
            deep: true,
            handler() {
                this.checkDataChanges();
            }
        },
        validate: {
            deep: true,
            handler(newVal) {
                if (newVal.length !== 0) {
                    this.tableData = JSON.parse(JSON.stringify(newVal));
                    this.setOriginalData();
                }
            }
        }
    },
    methods: {
        setOriginalData() {
            this.originalTableData = JSON.parse(JSON.stringify(this.tableData));
        },
        checkDataChanges() {
            const hasChanged = !isEqual(this.originalTableData, this.tableData);
            this.$emit("dataChanged", hasChanged);
        },
        querySearch(queryString, cb) {
            let validateOptions = this.validateOptions;
            let results = queryString
                ? validateOptions.filter(this.createFilter(queryString))
                : validateOptions;
            cb(results);
        },
        createFilter(queryString) {
            return validateOptions => {
                return (
                    validateOptions.value
                        .toLowerCase()
                        .indexOf(queryString.toLowerCase()) === 0
                );
            };
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave(row) {
            this.currentRow = "";
        },
        handleEdit(index, row) {
            this.tableData.push({
                expect: "",
                actual: "",
                comparator: "equals",
                type: 1,
                desc: ""
            });
        },
        handleCopy(index, row) {
            this.tableData.splice(index + 1, 0, {
                expect: row.expect,
                actual: row.actual,
                comparator: row.comparator,
                type: row.type,
                desc: row.desc
            });
        },
        handleDelete(index, row) {
            this.tableData.splice(index, 1);
        },
        parseValidate() {
            let validate = {
                validate: []
            };
            for (let content of this.tableData) {
                if (content["actual"] !== "") {
                    let obj = {};
                    const expect = this.parseType(
                        content["type"],
                        content["expect"]
                    );
                    if (expect === "exception") {
                        continue;
                    }
                    obj[content["comparator"]] = [
                        content["actual"],
                        expect,
                        content["desc"]
                    ];
                    validate.validate.push(obj);
                }
            }
            return validate;
        },
        // 类型转换
        parseType(type, value) {
            let tempValue;
            const msg =
                value +
                " => " +
                this.dataTypeOptions[type - 1].label +
                " 转换异常, 该数据自动剔除";
            switch (type) {
                case 1:
                    tempValue = value;
                    break;
                case 2:
                    // 包含$是引用类型，可以是任意类型
                    if (value.indexOf("$") !== -1) {
                        tempValue = value;
                    } else {
                        tempValue = parseInt(value);
                    }
                    break;
                case 3:
                    tempValue = parseFloat(value);
                    break;
                case 4:
                    if (value === "False" || value === "True") {
                        let bool = {
                            True: true,
                            False: false
                        };
                        tempValue = bool[value];
                    } else {
                        this.$notify.error({
                            title: "类型转换错误",
                            message: msg,
                            duration: 2000
                        });
                        return "exception";
                    }
                    break;
                case 5:
                case 6:
                    try {
                        tempValue = JSON.parse(value);
                    } catch (err) {
                        // 包含$是引用类型，可以是任意类型
                        if (value.indexOf("$") !== -1) {
                            tempValue = value;
                        } else {
                            tempValue = false;
                        }
                    }
                    break;
                case 7:
                    // None转null
                    if (value === null) {
                        tempValue = null;
                    } else if (value.indexOf("$") !== -1) {
                        tempValue = value;
                    } else {
                        this.$notify.error({
                            title: "类型转换错误",
                            message: msg,
                            duration: 2000
                        });
                        return "exception";
                    }
                    break;
            }
            if (
                tempValue !== 0 &&
                !tempValue &&
                type !== 4 &&
                type !== 1 &&
                type !== 7
            ) {
                this.$notify.error({
                    title: "类型转换错误",
                    message: msg,
                    duration: 2000
                });
                return "exception";
            }
            return tempValue;
        }
    },
    mounted() {
        this.setOriginalData();
    }
};
</script>

<style scoped></style>
