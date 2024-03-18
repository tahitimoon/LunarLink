<template>
    <el-container>
        <el-header style="background: #ffffff; padding: 0; height: 50px">
            <div class="nav-api-header">
                <div
                    style="display: flex; padding-top: 10px; margin-left: 10px; align-items: center;"
                >
                    <el-button
                        type="primary"
                        size="small"
                        icon="el-icon-circle-plus-outline"
                        @click="handleAddTask"
                        >添加任务</el-button
                    >
                    <el-button
                        :disabled="!addTasks"
                        type="text"
                        style="position: absolute; right: 30px"
                        @click="addTasks = false"
                        >返回列表</el-button
                    >
                </div>
            </div>
        </el-header>

        <el-container>
            <el-header
                v-if="!addTasks"
                style="padding-top: 10px; height: 50px; margin-left: 10px;"
            >
                <div class="task__header">
                    <div class="task__header--item">
                        <el-input
                            clearable
                            size="small"
                            placeholder="请输入任务名称"
                            v-model="searchTaskName"
                            style="width: 300px; margin-left: -10px"
                        >
                        </el-input>
                    </div>

                    <div class="task__header--item">
                        <el-select
                            v-model="selectUser"
                            placeholder="请选择创建人"
                            filterable
                            size="small"
                            style="width: 100px"
                        >
                            <el-option
                                v-for="(item, index) in users"
                                :key="index"
                                :label="item.label"
                                :value="item.value"
                            ></el-option>
                        </el-select>
                        <el-button
                            plain
                            size="small"
                            style="margin-left: 10px"
                            icon="el-icon-refresh"
                            @click="resetSearch"
                            >重置</el-button
                        >
                    </div>
                </div>
            </el-header>

            <el-main style="padding: 0; margin-left: 10px; margin-top: 10px">
                <div class="tasks__body__table">
                    <el-table
                        highlight-current-row
                        stripe
                        v-if="!addTasks"
                        :data="tasksData.results"
                        v-loading="loading"
                        height="calc(100%)"
                        @cell-mouse-enter="cellMouseEnter"
                        @cell-mouse-leave="cellMouseLeave"
                    >
                        <el-table-column label="任务ID" width="80">
                            <template slot-scope="scope">
                                <div>{{ scope.row.id }}</div>
                            </template>
                        </el-table-column>

                        <el-table-column label="任务名称" width="300">
                            <template slot-scope="scope">
                                <div
                                    :title="scope.row.name"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    {{ scope.row.name }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="时间配置" width="120">
                            <template slot-scope="scope">
                                <div>{{ scope.row.kwargs.crontab }}</div>
                            </template>
                        </el-table-column>

                        <el-table-column label="下次执行时间" width="170">
                            <template slot-scope="scope">
                                <div>
                                    {{
                                        (scope.row.kwargs.next_execute_time
                                            ? scope.row.kwargs.next_execute_time
                                            : "") | timestampToTime
                                    }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="运行配置" width="180">
                            <template slot-scope="scope">
                                <div
                                    :title="scope.row.kwargs.config"
                                    style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                >
                                    {{
                                        scope.row.kwargs.config === "请选择"
                                            ? "用例配置"
                                            : scope.row.kwargs.config
                                    }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="通知策略" width="100">
                            <template slot-scope="scope">
                                <div>{{ scope.row.kwargs.strategy }}</div>
                            </template>
                        </el-table-column>

                        <el-table-column label="已运行" width="80">
                            <template slot-scope="scope">
                                <el-tag type="success">{{
                                    scope.row.total_run_count
                                }}</el-tag>
                            </template>
                        </el-table-column>

                        <el-table-column label="状态" width="80">
                            <template slot-scope="scope">
                                <el-switch
                                    v-model="scope.row.enabled"
                                    active-color="#13ce66"
                                    @change="
                                        handleSwitchChange(
                                            scope.row.id,
                                            scope.row.enabled
                                        )
                                    "
                                    inactive-color="#ff4949"
                                ></el-switch>
                            </template>
                        </el-table-column>

                        <el-table-column label="创建人" width="100">
                            <template slot-scope="scope">
                                <div>{{ scope.row.kwargs.creator }}</div>
                            </template>
                        </el-table-column>

                        <el-table-column label="更新人" width="100">
                            <template slot-scope="scope">
                                <div>
                                    {{
                                        scope.row.kwargs.updater
                                            ? scope.row.kwargs.updater
                                            : "-"
                                    }}
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column label="任务操作">
                            <template slot-scope="scope">
                                <el-row v-show="currentRow === scope.row">
                                    <div
                                        style="display: flex; align-items: center;"
                                    >
                                        <el-button
                                            type="info"
                                            icon="el-icon-edit"
                                            title="编辑"
                                            circle
                                            size="mini"
                                            @click="
                                                handleEditSchedule(
                                                    scope.row.id,
                                                    scope.row
                                                )
                                            "
                                        ></el-button>
                                        <el-button
                                            type="success"
                                            icon="el-icon-document-copy"
                                            title="复制"
                                            circle
                                            size="mini"
                                            @click="
                                                handleCopyTask(
                                                    scope.row.id,
                                                    scope.row.name
                                                )
                                            "
                                        ></el-button>
                                        <el-button
                                            type="primary"
                                            icon="el-icon-caret-right"
                                            title="手动触发任务"
                                            circle
                                            size="mini"
                                            @click="runTask(scope.row.id)"
                                        ></el-button>
                                        <el-button
                                            type="danger"
                                            icon="el-icon-delete"
                                            title="删除"
                                            circle
                                            size="mini"
                                            @click="delTasks(scope.row.id)"
                                        ></el-button>
                                    </div>
                                </el-row>
                            </template>
                        </el-table-column>
                    </el-table>
                    <div class="pagination-container">
                        <el-pagination
                            v-show="tasksData.count !== 0 && !addTasks"
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                            :current-page.sync="currentPage"
                            :page-sizes="[10, 20, 30, 40]"
                            :page-size="pageSize"
                            :pager-count="5"
                            :total="tasksData.count"
                            layout="total, sizes, prev, pager, next, jumper"
                            background
                        ></el-pagination>
                    </div>
                </div>
            </el-main>
            <add-tasks
                v-if="addTasks"
                @changeStatus="changeStatus"
                :rule-form="ruleForm"
                :config-options="configOptions"
                :args="args"
                :schedule-id="scheduleId"
                :current-page.sync="currentPage"
                :page-size.sync="pageSize"
            ></add-tasks>
        </el-container>
    </el-container>
</template>

<script>
import AddTasks from "@/pages/task/AddTasks";
export default {
    name: "Task",
    components: {
        AddTasks
    },
    data() {
        return {
            addTasks: false,
            searchDebounce: null,
            scheduleId: "",
            currentPage: 1,
            pageSize: 10,
            currentRow: "",
            tasksData: {
                count: 0,
                results: []
            },
            ruleForm: {
                switch: true,
                crontab: "",
                ci_project_ids: "",
                strategy: "始终发送",
                receiver: "",
                mail_cc: "",
                name: "",
                sensitive_keys: "",
                self_error: "",
                fail_count: 1,
                webhook: "",
                config: "请选择",
                ci_env: "请选择",
                is_parallel: false
            },
            args: [],
            users: [],
            selectUser: this.$store.state.name,
            searchTaskName: "",
            configOptions: [],
            loading: true
        };
    },
    methods: {
        handleAddTask() {
            this.scheduleId = ""; // 每次添加任务时，清空scheduleId，不然编辑任务后，再添加任务，会走调用接口
            this.addTasks = true;
            this.ruleForm = {
                switch: true,
                crontab: "",
                strategy: "始终发送",
                receiver: "",
                mail_cc: "",
                name: "",
                sensitive_keys: "",
                self_error: "",
                fail_count: 1,
                webhook: "",
                ci_project_ids: "",
                config: "请选择",
                ci_env: "请选择",
                is_parallel: false
            };
            this.args = [];
            this.initConfig();
        },
        delTasks(taskId) {
            this.$confirm("此操作将永久删除任务，是否继续？", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.delTasks(taskId).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getTaskList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        runTask(id) {
            this.$api.runTask(id).then(resp => {
                if (resp.success) {
                    this.$message.info({
                        message: resp.msg,
                        center: true
                    });
                } else {
                    this.$message.error({
                        message: resp.msg,
                        center: true
                    });
                }
            });
        },
        handleCurrentChange() {
            this.$api
                .getTaskPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        creator: this.selectUser,
                        project: this.$route.params.id
                    }
                })
                .then(resp => {
                    this.tasksData = resp;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.tasksData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .getTaskPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        creator: this.selectUser,
                        project: this.$route.params.id
                    }
                })
                .then(resp => {
                    this.tasksData = resp;
                });
        },
        getTaskList() {
            this.$api
                .taskList({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.$route.params.id,
                        creator: this.selectUser,
                        task_name: this.searchTaskName
                    }
                })
                .then(resp => {
                    this.tasksData = resp;
                    this.loading = false;
                });
        },
        handleSwitchChange(taskId, val) {
            this.$api.patchTask(taskId, { switch: val }).then(resp => {
                if (resp.success) {
                    this.$message.success(
                        val ? "定时任务已开启" : "定时任务已关闭"
                    );
                } else {
                    this.$message.error("定时任务修改失败");
                }
                this.getTaskList();
            });
        },
        handleEditSchedule(id, row) {
            // 激活addTasks组件
            this.addTasks = true;
            this.scheduleId = id;
            this.ruleForm["crontab"] = row.kwargs.crontab;
            this.ruleForm["strategy"] = row.kwargs.strategy;
            this.ruleForm["receiver"] = row.kwargs.receiver;
            this.ruleForm["mail_cc"] = row.kwargs.mail_cc;
            this.ruleForm["fail_count"] = row.kwargs.fail_count;
            this.ruleForm["self_error"] = row.kwargs.self_error;
            this.ruleForm["sensitive_keys"] = row.kwargs.sensitive_keys;
            this.ruleForm["webhook"] = row.kwargs.webhook;
            this.ruleForm["ci_project_ids"] = row.kwargs.ci_project_ids;
            this.ruleForm["updater"] = this.$store.state.name;
            this.ruleForm["creator"] = row.kwargs.creator;
            this.ruleForm["config"] = row.kwargs.config;
            this.ruleForm["ci_env"] = row.kwargs.ci_env;
            this.ruleForm["is_parallel"] = row.kwargs.is_parallel;
            this.ruleForm["name"] = row.name;
            this.ruleForm["switch"] = row.enabled;
            this.args = row.args;
            this.initConfig();
        },
        handleCopyTask(id, name) {
            this.$prompt("请输入任务名称", "提示", {
                closeOnClickModal: false,
                confirmButtonText: "确定",
                inputPattern: /^[\s\S]*\S[\s\S]*$/,
                inputErrorMessage: "任务名称不能为空",
                inputValue: name
            }).then(({ value }) => {
                this.$api.copyTask(id, { name: value }).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getTaskList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        changeStatus(value) {
            this.pageSize = 10;
            this.currentPage = 1;
            this.args = [];
            this.getTaskList();
            this.addTasks = value;
            this.ruleForm = {
                switch: true,
                crontab: "",
                strategy: "始终发送",
                receiver: "",
                mail_cc: "",
                name: "",
                sensitive_keys: "",
                self_error: "",
                fail_count: "",
                webhook: "",
                ci_project_ids: "",
                config: "请选择",
                ci_env: "请选择",
                is_parallel: false
            };
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        getUserList() {
            this.$api.getUserList().then(resp => {
                for (let i = 0; i < resp.length; i++) {
                    this.users.push({
                        label: resp[i].name,
                        value: resp[i].name
                    });
                }
                this.users.unshift({ label: "所有人", value: "" });
            });
        },
        resetSearch() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.searchTaskName = "";
            this.selectUser = this.$store.state.name;
            this.getTaskList();
        },
        initConfig() {
            this.$api.getAllConfig(this.$route.params.id).then(resp => {
                this.configOptions = resp;
                this.configOptions.unshift({ name: "请选择" });
            });
        },
        debouncedGetTasks() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getTaskList();
            }, 300);
        }
    },
    watch: {
        selectUser() {
            this.debouncedGetTasks();
        },
        searchTaskName() {
            this.debouncedGetTasks();
        }
    },
    mounted() {
        this.getUserList();
        this.getTaskList();
    }
};
</script>

<style scoped>
.task__header {
    display: flex;
    align-items: center;
    margin-left: -20px;
}

.task__header--item {
    display: flex;
    margin-left: 10px;
}

.tasks__body__table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 230px;
    top: 150px;
    margin-left: -20px;
    padding-bottom: 60px;
}
</style>
