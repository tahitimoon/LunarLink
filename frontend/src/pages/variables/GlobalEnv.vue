<template>
    <el-container>
        <el-header style="background: #fff; padding:0; height:50px;">
            <div>
                <div class="nav-api-header">
                    <div
                        style="display: flex; padding-top: 10px; margin-left: 10px;"
                    >
                        <el-button
                            type="primary"
                            size="small"
                            icon="el-icon-circle-plus-outline"
                            @click="
                                openFormModal('variablesForm', 'dialogVisible')
                            "
                            >新增变量</el-button
                        >
                        <el-button
                            type="danger"
                            icon="el-icon-delete"
                            size="small"
                            @click="delSelectionVariables"
                            :disabled="!isSelectVariables"
                            >批量删除</el-button
                        >
                    </div>
                </div>

                <el-dialog
                    title="添加变量"
                    width="30%"
                    :visible.sync="dialogVisible"
                    :close-on-click-modal="false"
                    :style="{ 'text-align': 'center' }"
                >
                    <el-form
                        :model="variablesForm"
                        :rules="rules"
                        ref="variablesForm"
                        label-width="100px"
                        class="project"
                    >
                        <el-form-item label="变量名" prop="key">
                            <el-input
                                v-model.trim="variablesForm.key"
                                clearable
                                placeholder="请输入变量名"
                            ></el-input>
                        </el-form-item>
                        <el-form-item label="变量值" prop="value">
                            <el-input
                                v-model.trim="variablesForm.value"
                                clearable
                                placeholder="请输入变量值"
                            ></el-input>
                        </el-form-item>
                        <el-form-item label="变量描述" prop="description">
                            <el-input
                                v-model.trim="variablesForm.description"
                                clearable
                                placeholder="请输入变量描述"
                            ></el-input>
                        </el-form-item>
                    </el-form>
                    <span
                        slot="footer"
                        class="dialog-footer"
                        style="display: flex; justify-content: flex-end;"
                    >
                        <el-button
                            @click="resetForm('variablesForm', 'dialogVisible')"
                            >取 消</el-button
                        >
                        <el-button
                            type="primary"
                            @click="handleConfirm('variablesForm')"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>

                <el-dialog
                    title="编辑变量"
                    :visible.sync="editDialogVisible"
                    :close-on-click-modal="false"
                    width="30%"
                    :style="{ 'text-align': 'center' }"
                >
                    <el-form
                        :model="editVariablesForm"
                        :rules="rules"
                        ref="editVariablesForm"
                        label-width="100px"
                        class="project"
                    >
                        <el-form-item label="变量名" prop="key">
                            <el-input
                                v-model.trim="editVariablesForm.key"
                                clearable
                                placeholder="请输入变量名"
                            ></el-input>
                        </el-form-item>
                        <el-form-item label="变量值" prop="value">
                            <el-input
                                v-model.trim="editVariablesForm.value"
                                clearable
                                placeholder="请输入变量值"
                            ></el-input>
                        </el-form-item>
                        <el-form-item label="变量描述" prop="description">
                            <el-input
                                v-model.trim="editVariablesForm.description"
                                clearable
                                placeholder="请输入变量描述"
                            ></el-input>
                        </el-form-item>
                    </el-form>
                    <span
                        slot="footer"
                        class="dialog-footer"
                        style="display: flex; justify-content: flex-end;"
                    >
                        <el-button
                            @click="
                                resetForm(
                                    'editVariablesForm',
                                    'editDialogVisible'
                                )
                            "
                            >取 消</el-button
                        >
                        <el-button
                            type="primary"
                            @click="handleEditConfirm('editVariablesForm')"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>
            </div>
        </el-header>

        <el-container>
            <el-header
                style="padding-top: 10px; margin-left: 10px; height: 50px"
            >
                <div class="env__header">
                    <div class="env__header--item">
                        <el-input
                            style="width: 300px"
                            size="small"
                            placeholder="请输入变量名称"
                            v-model="search"
                            clearable
                        >
                        </el-input>
                    </div>

                    <div class="env__header--item">
                        <el-button
                            plain
                            size="small"
                            icon="el-icon-refresh"
                            @click="resetSearch"
                            >重置</el-button
                        >
                    </div>
                </div>
            </el-header>

            <el-container>
                <el-main
                    style="padding: 0; margin-left: 10px; margin-top: 10px"
                >
                    <div class="env-body-table">
                        <el-table
                            highlight-current-row
                            stripe
                            :data="variablesData.results"
                            v-loading="loading"
                            height="calc(100%)"
                            @cell-mouse-enter="cellMouseEnter"
                            @cell-mouse-leave="cellMouseLeave"
                            @selection-change="handleSelectionChange"
                        >
                            <el-table-column
                                type="selection"
                                width="55"
                            ></el-table-column>

                            <el-table-column label="变量名" width="300">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.key"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{ scope.row.key }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="变量值">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.value"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{ scope.row.value }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="变量描述">
                                <template slot-scope="scope">
                                    <div
                                        :title="scope.row.description"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{ scope.row.description }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="更新时间">
                                <template slot-scope="scope">
                                    <div>
                                        {{
                                            scope.row.update_time
                                                | datetimeFormat
                                        }}
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="变量操作">
                                <template slot-scope="scope">
                                    <el-row v-show="currentRow === scope.row">
                                        <el-button
                                            type="info"
                                            icon="el-icon-edit"
                                            title="编辑"
                                            circle
                                            size="mini"
                                            @click="
                                                handleEditVariables(scope.row)
                                            "
                                        ></el-button>

                                        <el-button
                                            type="success"
                                            icon="el-icon-document-copy"
                                            title="复制"
                                            circle
                                            size="mini"
                                            @click="
                                                handleCopyVariables(scope.row)
                                            "
                                        ></el-button>

                                        <el-button
                                            v-show="variablesData.count !== 0"
                                            type="danger"
                                            icon="el-icon-delete"
                                            title="删除"
                                            circle
                                            size="mini"
                                            @click="
                                                handleDelVariables(scope.row.id)
                                            "
                                        ></el-button>
                                    </el-row>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination-container">
                            <el-pagination
                                v-show="variablesData.count !== 0"
                                background
                                @current-change="handleCurrentChange"
                                @size-change="handleSizeChange"
                                :current-page.sync="currentPage"
                                :page-sizes="[10, 20, 30, 40]"
                                :page-size="pageSize"
                                :pager-count="5"
                                layout="total, sizes, prev, pager, next, jumper"
                                :total="variablesData.count"
                            ></el-pagination>
                        </div>
                    </div>
                </el-main>
            </el-container>
        </el-container>
    </el-container>
</template>

<script>
export default {
    name: "GlobalEnv",
    data() {
        return {
            search: "",
            selectVariables: [],
            currentRow: "",
            currentPage: 1,
            pageSize: 10,
            variablesData: {
                count: 0,
                results: []
            },
            editDialogVisible: false,
            dialogVisible: false,
            searchDebounce: null,
            variablesForm: {
                key: "",
                value: "",
                project: this.$route.params.id
            },
            editVariablesForm: {
                id: "",
                key: "",
                value: "",
                description: ""
            },
            rules: {
                key: [
                    {
                        required: true,
                        message: "请输入变量名",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 100,
                        message: "最多不超过100个字符",
                        trigger: "blur"
                    }
                ],
                value: [
                    {
                        required: true,
                        message: "请输入变量值",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 1024,
                        message: "最多不超过1024个字符",
                        trigger: "blur"
                    }
                ],
                description: [
                    {
                        required: false,
                        message: "请输入变量描述",
                        trigger: "blur"
                    },
                    {
                        min: 0,
                        max: 100,
                        message: "最多不超过100个字符",
                        trigger: "blur"
                    }
                ]
            },
            loading: true,
            isSelectVariables: false
        };
    },
    methods: {
        debouncedGetVariablesList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getVariablesList();
            }, 300);
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        handleEditVariables(row) {
            this.editVariablesForm = {
                key: row.key,
                value: row.value,
                id: row.id,
                description: row.description
            };
            this.editDialogVisible = true;
        },
        handleCopyVariables(row) {
            this.dialogVisible = true;
            this.variablesForm.key = row.key;
            this.variablesForm.value = row.value;
            this.variablesForm.description = row.description;
        },
        handleDelVariables(variableId) {
            this.$confirm("此操作将永久删除全局变量，是否继续?", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.deleteVariables(variableId).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getVariablesList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        handleSelectionChange(val) {
            this.selectVariables = val;
            // 更新是否已经选择Variables, 依赖这个属性来判断是否禁用批量删除按钮
            this.isSelectVariables = this.selectVariables.length > 0;
        },
        handleCurrentChange() {
            this.$api
                .getVariablesPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.variablesForm.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.variablesData = resp;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.variablesData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .getVariablesPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        project: this.variablesForm.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.variablesData = resp;
                });
        },
        delSelectionVariables() {
            if (this.selectVariables.length !== 0) {
                this.$confirm(
                    "此操作将永久删除勾选的全局变量，是否继续？",
                    "提示",
                    {
                        confirmButtonText: "确定",
                        cancelButtonText: "取消",
                        type: "warning"
                    }
                ).then(() => {
                    this.$api
                        .delAllVariables({ data: this.selectVariables })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success(resp.msg);
                                this.getVariablesList();
                            } else {
                                this.$message.error(resp.msg);
                            }
                        });
                });
            } else {
                this.$notify.warning({
                    title: "提示",
                    message: "请至少勾选一个全局变量",
                    duration: this.$store.state.duration
                });
            }
        },
        handleConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.dialogVisible = false;
                    this.$api.addVariables(this.variablesForm).then(resp => {
                        if (resp.success) {
                            this.variablesForm.key = "";
                            this.variablesForm.value = "";
                            this.$message.success(resp.msg);
                            this.getVariablesList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
                }
            });
        },
        // 重置表单
        resetForm(formName, showFlag) {
            this[showFlag] = false;
            this.$refs[formName].resetFields();
            for (const key in this[formName]) {
                if (this[formName].hasOwnProperty(key) && key !== "project") {
                    this[formName][key] = "";
                }
            }
        },
        // 唤起表单弹窗
        openFormModal(formName, showFlag) {
            for (const key in this[formName]) {
                if (this[formName].hasOwnProperty(key) && key !== "project") {
                    this[formName][key] = "";
                }
            }
            this[showFlag] = true;
        },
        handleEditConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.editDialogVisible = false;
                    this.$api
                        .updateVariables(
                            this.$route.params.id,
                            this.editVariablesForm
                        )
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success(resp.msg);
                                this.getVariablesList();
                            } else {
                                this.$message.error({
                                    message: resp.msg,
                                    duration: this.$store.state.duration
                                });
                            }
                        });
                }
            });
        },
        getVariablesList() {
            this.$api
                .variablesList({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.variablesForm.project,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.variablesData = resp;
                    this.loading = false;
                });
        },
        resetSearch() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.search = "";
            this.getVariablesList();
        }
    },
    watch: {
        search() {
            this.debouncedGetVariablesList();
        }
    },
    mounted() {
        this.getVariablesList();
    }
};
</script>

<style scoped>
.env__header {
    display: flex;
    align-items: center;
    margin-left: -30px;
}

.env__header--item {
    display: flex;
    margin-left: 10px;
}

.env-body-table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 220px;
    top: 150px;
    margin-left: -10px;
    padding-bottom: 60px;
}
</style>
