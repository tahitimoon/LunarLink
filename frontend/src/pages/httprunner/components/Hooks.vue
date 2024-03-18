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
        <el-table-column label="测试之前执行的方法" width="500">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.setup"
                    placeholder="${ setup_hooks function($request, *args, **kwargs) }"
                ></el-input>
            </template>
        </el-table-column>

        <el-table-column label="测试之后执行的方法" width="500">
            <template v-slot="scope">
                <el-input
                    clearable
                    v-model.trim="scope.row.teardown"
                    placeholder="${ teardown_hooks function($response, *args, **kwargs) }"
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
                        @click="addHooks"
                    ></el-button>
                    <el-button
                        icon="el-icon-delete"
                        size="mini"
                        type="danger"
                        v-show="scope.$index !== 0"
                        @click="deleteHooks(scope.$index)"
                    ></el-button>
                </el-row>
            </template>
        </el-table-column>
    </el-table>
</template>

<script>
import { isEqual } from "lodash";

export default {
    name: "Hooks",
    data() {
        return {
            currentRow: "",
            originalTableData: [],
            tableData: [
                {
                    setup: "",
                    teardown: ""
                }
            ]
        };
    },
    props: {
        save: Boolean,
        hooks: {
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
            this.$emit("hooks", this.parse_hooks(), this.tableData);
        },
        tableData: {
            deep: true,
            handler() {
                this.checkDataChanges();
            }
        },
        hooks: {
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
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave(row) {
            this.currentRow = "";
        },
        addHooks(index, row, flag) {
            this.tableData.push({
                setup: "",
                teardown: ""
            });
        },
        deleteHooks(index, row) {
            this.tableData.splice(index, 1);
        },
        parse_hooks() {
            let hooks = {
                setup_hooks: [],
                teardown_hooks: []
            };
            for (let content of this.tableData) {
                if (content.setup !== "") {
                    hooks.setup_hooks.push(content.setup);
                }
                if (content.teardown !== "") {
                    hooks.teardown_hooks.push(content.teardown);
                }
            }
            return hooks;
        }
    },
    mounted() {
        this.setOriginalData();
    }
};
</script>

<style scoped></style>
