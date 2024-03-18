<template>
    <el-container>
        <template v-if="!next">
            <el-main style="padding-top: 0">
                <div style="margin-top: 10px">
                    <el-col :span="12">
                        <el-form
                            :model="ruleForm"
                            :rules="rules"
                            ref="ruleForm"
                            label-width="100px"
                        >
                            <el-form-item label="任务名称" prop="name">
                                <el-input
                                    clearable
                                    v-model.trim="ruleForm.name"
                                    placeholder="请输入任务名称"
                                ></el-input>
                            </el-form-item>

                            <el-form-item label="时间配置" prop="crontab">
                                <el-input
                                    readonly
                                    v-model="ruleForm.crontab"
                                    placeholder="请配置cron表达式"
                                >
                                    <el-button
                                        slot="append"
                                        icon="el-icon-edit"
                                        type="success"
                                        plain
                                        @click="showDialog"
                                        >生成</el-button
                                    >
                                </el-input>
                            </el-form-item>

                            <el-dialog
                                title="生成 cron"
                                :visible.sync="showCron"
                                :close-on-click-modal="false"
                            >
                                <vcrontab
                                    @hide="showCron = false"
                                    @fill="crontabFill"
                                    :expression="expression"
                                ></vcrontab>
                            </el-dialog>

                            <el-form-item label="运行配置" prop="config">
                                <el-select
                                    clearable
                                    v-model="ruleForm.config"
                                    value-key="id"
                                    placeholder="请选择"
                                    size="small"
                                >
                                    <el-option
                                        v-for="item in configOptions"
                                        :key="item.id"
                                        :label="item.name"
                                        :value="item.name"
                                    ></el-option>
                                </el-select>
                                <el-tooltip placement="top">
                                    <div slot="content">
                                        指定任务运行时的配置<br />请选择：使用用例中的配置
                                        <br />选择其他配置：当前选择配置覆盖用例的配置<br />
                                    </div>
                                    <span class="el-icon-question"></span>
                                </el-tooltip>
                            </el-form-item>

                            <el-form-item label="任务状态" prop="switch">
                                <el-switch
                                    v-model="ruleForm.switch"
                                ></el-switch>
                            </el-form-item>

                            <el-form-item label="运行模式" prop="is_parallel">
                                <template>
                                    <el-radio
                                        v-model="ruleForm.is_parallel"
                                        :label="false"
                                        >串行</el-radio
                                    >
                                    <el-radio
                                        v-model="ruleForm.is_parallel"
                                        :label="true"
                                        >并行</el-radio
                                    >
                                    <el-tooltip placement="top">
                                        <div slot="content">
                                            用例运行模式<br />任务中的用例默认是一个接一个运行；并行时，同时执行用例，不分先后
                                        </div>
                                        <span class="el-icon-question"></span>
                                    </el-tooltip>
                                </template>
                            </el-form-item>

                            <el-form-item label="通知策略" prop="strategy">
                                <el-radio-group v-model="ruleForm.strategy">
                                    <el-radio label="始终发送"></el-radio>
                                    <el-radio label="仅失败发送"></el-radio>
                                    <el-radio label="从不发送"></el-radio>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="邮件接收人" prop="receiver">
                                <el-input
                                    type="textarea"
                                    v-model="ruleForm.receiver"
                                    placeholder="多个接收人以;分隔"
                                    clearable
                                    :autosize="{
                                        minRows: 1,
                                        maxRows: 3
                                    }"
                                ></el-input>
                            </el-form-item>

                            <el-form-item label="邮件抄送人" prop="mail_cc">
                                <el-input
                                    type="textarea"
                                    v-model="ruleForm.mail_cc"
                                    placeholder="多个抄送人以;分隔"
                                    clearable
                                    :autosize="{
                                        minRows: 1,
                                        maxRows: 3
                                    }"
                                ></el-input>
                            </el-form-item>

                            <el-form-item label="webhook" prop="webhook">
                                <el-input
                                    clearable
                                    placeholder="企微机器人webhook地址, 多个时换行即可"
                                    type="textarea"
                                    v-model="ruleForm.webhook"
                                    :autosize="{
                                        minRows: 1,
                                        maxRows: 3
                                    }"
                                ></el-input>
                            </el-form-item>

                            <el-form-item>
                                <div style="display: flex;">
                                    <el-button
                                        type="primary"
                                        @click="submitForm('ruleForm')"
                                        >下一步</el-button
                                    >
                                    <el-button @click="resetForm('ruleForm')"
                                        >重置</el-button
                                    >
                                </div>
                            </el-form-item>
                        </el-form>
                    </el-col>
                </div>
            </el-main>
        </template>

        <template v-if="next">
            <el-aside style="width: 250px; margin-top: 10px">
                <div class="nav-api-side">
                    <div class="api-tree">
                        <el-input
                            clearable
                            placeholder="请输入关键字进行过滤"
                            v-model="filterText"
                            size="medium"
                            prefix-icon="el-icon-search"
                        ></el-input>
                        <el-tree
                            @node-click="handleNodeClick"
                            :data="dataTree"
                            node-key="id"
                            :default-expand-all="false"
                            :expand-on-click-node="false"
                            highlight-current
                            :filter-node-method="filterNode"
                            ref="tree2"
                        >
                            <span
                                class="custom-tree-node"
                                slot-scope="{ node, data }"
                            >
                                <span class="custom-tree-node-span">
                                    <i
                                        v-if="node.childNodes.length > 0"
                                        class="el-icon-folder-opened"
                                    ></i>
                                    <i v-else class="el-icon-folder"></i
                                    >&nbsp;&nbsp;{{ node.label }}
                                </span>

                                <span style="flex-shrink: 0; margin-left: 5px;">
                                    <el-badge
                                        :value="data.data_count"
                                        :max="99"
                                        type="primary"
                                    ></el-badge>
                                </span>
                            </span>
                        </el-tree>
                    </div>
                </div>
            </el-aside>

            <el-main style="padding-top: 0">
                <div>
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <div style="display: flex">
                                <el-input
                                    style="width: 300px"
                                    size="medium"
                                    placeholder="请输入用例名称"
                                    v-model="search"
                                    clearable
                                >
                                </el-input>
                                <div style="margin-left: 10px">
                                    <el-button
                                        plain
                                        size="medium"
                                        icon="el-icon-refresh"
                                        @click="resetSearch"
                                        >重置</el-button
                                    >
                                </div>
                                <div style="margin-left: 10px">
                                    <el-select
                                        v-model="creator"
                                        placeholder="请选择创建人"
                                        size="medium"
                                        style="width: 100px"
                                    >
                                        <el-option
                                            v-for="item in creatorOptions"
                                            :key="item.value"
                                            :label="item.label"
                                            :value="item.value"
                                        >
                                        </el-option>
                                    </el-select>
                                </div>
                            </div>
                        </el-col>
                        <el-col :span="12">
                            <div style="display: flex;">
                                <el-button
                                    size="medium"
                                    v-if="testData.length > 0"
                                    @click="next = false"
                                    >上一步</el-button
                                >
                                <el-button
                                    size="medium"
                                    type="primary"
                                    v-if="testData.length > 0"
                                    @click="saveTask"
                                    >保存</el-button
                                >
                            </div>
                        </el-col>
                    </el-row>
                </div>

                <div style="position: relative; height: 680px;">
                    <div
                        style="height: calc(100% - 50px); overflow-y: auto; overflow-x: hidden;"
                    >
                        <el-row :gutter="20">
                            <el-col :span="12">
                                <div
                                    v-for="(item, index) in suiteData.results"
                                    style="cursor: pointer; margin-top: 10px; overflow: auto"
                                    draggable="true"
                                    @dragstart="
                                        currentSuite = JSON.parse(
                                            JSON.stringify(item)
                                        )
                                    "
                                    :key="index"
                                >
                                    <div class="block block_options">
                                        <span
                                            class="block-method block_method_options block_method_color"
                                            >Case</span
                                        >
                                        <span class="block_name">{{
                                            item.name
                                        }}</span>
                                        <i
                                            class="el-icon-success"
                                            style="color: green; padding: 15px"
                                            v-if="item.tasks.length > 0"
                                            :title="
                                                '已加入定时任务：' +
                                                    item.tasks
                                                        .map(task => task.name)
                                                        .join(', ')
                                            "
                                        ></i>
                                    </div>
                                </div>
                            </el-col>
                            <el-col :span="12">
                                <div
                                    @drop="drop($event)"
                                    @dragover="allowDrop($event)"
                                >
                                    <span
                                        v-if="testData.length === 0"
                                        style="color: red"
                                        >温馨提示：<br />从左边拖拽用例至此区域组成任务列表<br />上下拖动此区域任务调整监控调用顺序</span
                                    >
                                    <div>
                                        <draggable
                                            v-model="testData"
                                            @end="dragEnd"
                                            @start="length = testData.length"
                                            :animation="200"
                                        >
                                            <div
                                                v-for="(test,
                                                index) in testData"
                                                :key="index"
                                                class="block block_test"
                                                @mousemove="currentTest = index"
                                            >
                                                <span
                                                    class="block-method block_method_test block_method_color"
                                                    >Task</span
                                                >
                                                <span class="block-test-name">{{
                                                    test.name
                                                }}</span>
                                                <el-button
                                                    style="position: absolute; right: 12px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="danger"
                                                    icon="el-icon-delete"
                                                    title="删除"
                                                    circle
                                                    size="mini"
                                                    @click="
                                                        testData.splice(
                                                            index,
                                                            1
                                                        )
                                                    "
                                                ></el-button>
                                            </div>
                                        </draggable>
                                    </div>
                                </div>
                            </el-col>
                        </el-row>
                    </div>
                    <div class="pagination-container">
                        <el-pagination
                            v-show="suiteData.count !== 0"
                            background
                            @current-change="handlePageChange"
                            @size-change="handleSizeChange"
                            :current-page.sync="currentPage"
                            :page-sizes="[10, 15, 20]"
                            :page-size="pageSize"
                            :pager-count="5"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="suiteData.count"
                            style="text-align: center"
                        ></el-pagination>
                    </div>
                </div>
            </el-main>
        </template>
    </el-container>
</template>

<script>
import draggable from "vuedraggable";
import vcrontab from "@/pages/vcrontab/Crontab";
import { isNumArray } from "@/validator";

export default {
    name: "AddTasks",
    components: {
        draggable,
        vcrontab
    },
    props: {
        ruleForm: {
            required: false
        },
        args: {
            required: true
        },
        scheduleId: {
            required: true
        },
        configOptions: {
            required: true,
            type: Array
        }
    },
    data() {
        return {
            creator: this.$store.state.name,
            creatorOptions: [],
            searchType: "1", // 1：根据用例名称搜索
            currentTest: "",
            length: 0,
            testData: [],
            currentSuite: "",
            search: "",
            next: false,
            expression: "",
            showCron: false,
            node: "",
            currentPage: 1,
            pageSize: 10,
            filterText: "",
            expand: "&#xe65f;",
            dataTree: [],
            suiteData: {
                count: 0,
                results: []
            },
            rules: {
                name: [
                    {
                        required: true,
                        message: "请输入任务名称",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 50,
                        message: "长度在 1 到 50 个字符",
                        trigger: "blur"
                    }
                ],
                crontab: [
                    {
                        required: true,
                        message: "请配置cron表达式",
                        trigger: "blur"
                    }
                ],
                ci_project_ids: [
                    {
                        required: false,
                        message: "请选择正确的ci_project_ids",
                        trigger: "blur"
                    },
                    {
                        validator: isNumArray,
                        trigger: "blur"
                    }
                ]
            },
            editTestCaseActivate: false
        };
    },
    methods: {
        crontabFill(value) {
            //确定后回传的值
            this.ruleForm.crontab = value;
        },
        showDialog() {
            //传入的 cron 表达式，可以反解析到 UI 上
            this.expression = this.ruleForm.crontab;
            this.showCron = true;
        },
        saveTask() {
            let task = [];
            for (let value of this.testData) {
                task.push(value.id);
            }
            let form = this.ruleForm;
            form["data"] = task;
            form["project"] = this.$route.params.id;
            // 新增
            if (this.scheduleId === "") {
                this.$api.addTask(form).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.$emit("changeStatus", false);
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
                // 修改
            } else {
                this.$api.updateTask(this.scheduleId, form).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.$emit("changeStatus", false);
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            }
        },
        dragEnd() {
            if (this.testData.length > this.length) {
                this.testData.splice(this.length, 1);
            }
        },
        drop(event) {
            event.preventDefault();
            this.testData.push(this.currentSuite);
        },
        allowDrop(event) {
            event.preventDefault();
        },
        handlePageChange() {
            this.$api
                .getTestPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        node: this.node,
                        project: this.$route.params.id,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.suiteData = resp;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.suiteData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .getTestPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        node: this.node,
                        project: this.$route.params.id,
                        search: this.search,
                        creator: this.creator,
                        searchType: this.searchType
                    }
                })
                .then(resp => {
                    this.suiteData = resp;
                });
        },
        handleCurrentChange() {
            this.$api
                .getTestPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.$route.params.id,
                        node: this.node,
                        search: this.search,
                        creator: this.creator,
                        searchType: this.searchType
                    }
                })
                .then(resp => {
                    this.suiteData = resp;
                });
        },
        submitForm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.next = true;
                } else {
                    return false;
                }
            });
            this.testData = this.args;
            // 用map遍历args的所有caseId, 如果和用例中的id相等, 就返回该用例的全部信息
            // 用map, filter过滤, case的数据在第二页时, 会导致name=undefined
            // this.testData = this.args.map(caseId=> this.suiteData.results.filter(testCase=> testCase.id === caseId)[0]);
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        getTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 2 } })
                .then(resp => {
                    this.dataTree = resp.tree;
                });
        },
        handleNodeClick(node) {
            this.node = node.id;
            this.getTestList();
        },
        getTestList() {
            this.$api
                .testList({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        project: this.$route.params.id,
                        node: this.node,
                        search: this.search,
                        creator: this.creator,
                        searchType: this.searchType
                    }
                })
                .then(resp => {
                    this.suiteData = resp;
                });
        },
        debouncedGetTestList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getTestList();
            }, 300);
        },
        resetSearch() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.search = "";
            this.node = "";
            this.creator = this.$store.state.name;
        },
        getUserList() {
            this.$api.getUserList().then(resp => {
                for (let i = 0; i < resp.length; i++) {
                    this.creatorOptions.push({
                        label: resp[i].name,
                        value: resp[i].name
                    });
                }
                this.creatorOptions.unshift({ label: "所有人", value: "" });
            });
        }
    },
    watch: {
        search() {
            this.debouncedGetTestList();
        },
        creator() {
            this.debouncedGetTestList();
        },
        filterText(val) {
            this.$refs.tree2.filter(val);
        }
    },
    mounted() {
        this.getTree();
        this.getTestList();
        this.getUserList();
    }
};
</script>

<style scoped>
.block_test {
    margin-top: 10px;
    border: 1px solid #49cc90;
    background-color: rgba(236, 248, 238, 0.4);
}

.block_method_test {
    background-color: #304056;
}

.block-test-name {
    width: 700px;
    padding-left: 10px;
    font-family: Open Sans, sans-serif;
    color: #3b4151;
    border: none;
    outline: none;
    background: rgba(236, 248, 238, 0.4);
}

.pagination-container {
    display: flex;
    justify-content: left;
    align-items: center;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
}
</style>
