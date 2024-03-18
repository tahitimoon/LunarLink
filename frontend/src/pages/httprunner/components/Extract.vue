<template>
    <el-table
        highlight-current-row
        stripe
        :height="height"
        :data="tableData"
        style="width: 100%"
        @cell-mouse-enter="cellMouseEnter"
        @cell-mouse-leave="cellMouseLeave"
        :cell-style="{ paddingTop: '4px', paddingBottom: '4px' }"
    >
        <el-table-column label="变量名" width="300">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.key"
                    placeholder="接受提取返回值后的变量名"
                ></el-input>
            </template>
        </el-table-column>
        <el-table-column label="提取表达式" width="420">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.value"
                    placeholder="提取表达式"
                ></el-input>
            </template>
        </el-table-column>
        <el-table-column label="描述" width="375">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.desc"
                    placeholder="提取值简要描述"
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
                        @click="handleEdit(scope.$index, scope.row)"
                    ></el-button>
                    <el-button
                        icon="el-icon-document-copy"
                        size="mini"
                        type="info"
                        @click="handleCopy(scope.$index, scope.row)"
                    ></el-button>
                    <el-button
                        icon="el-icon-delete"
                        size="mini"
                        type="danger"
                        v-show="scope.$index !== 0"
                        @click="handleDelete(scope.$index, scope.row)"
                    ></el-button>
                </el-row>
            </template>
        </el-table-column>
    </el-table>
</template>

<script>
import bus from "@/util/bus";
import { isEqual } from "lodash";

export default {
    name: "Extract",
    data() {
        return {
            currentRow: "",
            originalTableData: [],
            tableData: [
                {
                    key: "",
                    value: "",
                    desc: ""
                }
            ]
        };
    },
    props: {
        save: Boolean,
        extract: {
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
            this.$emit("extract", this.parseExtract(), this.tableData);
        },
        tableData: {
            deep: true,
            handler() {
                this.checkDataChanges();
            }
        },
        extract: {
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
        // 提取格式化
        parseExtract() {
            let extract = {
                extract: [],
                desc: {}
            };
            for (let content of this.tableData) {
                const key = content["key"];
                const value = content["value"];
                if (key !== "" && value !== "") {
                    let obj = {};
                    obj[key] = value;
                    extract.extract.push(obj);
                    extract.desc[key] = content["desc"];
                }
            }
            return extract;
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave(row) {
            this.currentRow = "";
        },
        handleEdit(index, row) {
            this.tableData.push({
                key: "",
                value: "",
                desc: ""
            });
        },
        handleCopy(index, row) {
            this.tableData.splice(index + 1, 0, {
                key: row.key,
                value: row.value,
                desc: row.desc
            });
        },
        handleDelete(index, row) {
            this.tableData.splice(index, 1);
        }
    },
    mounted() {
        bus.$on("extractRequest", extractObj => {
            // 当提取列表为空时, 先删除第一个
            if (
                this.tableData.length === 1 &&
                this.tableData[0].key === "" &&
                this.tableData[0].value === ""
            ) {
                this.tableData.pop();
            }
            this.tableData.push(extractObj);
        });

        this.setOriginalData();
    },
    beforeDestroy() {
        bus.$off("extractRequest");
    }
};
</script>

<style scoped></style>
