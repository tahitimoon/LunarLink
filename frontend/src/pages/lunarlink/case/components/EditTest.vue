<template>
    <el-container>
        <el-aside
            v-show="!editTestStepActivate"
            style="width: 250px; margin-top:10px;"
        >
            <div class="nav-api-side">
                <div class="api-tree">
                    <el-input
                        placeholder="请输入关键字进行过滤"
                        v-model="filterText"
                        size="medium"
                        clearable
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
        <el-container class="loading-container">
            <el-main v-loading="loading" style="padding: 20px 20px 0px 20px;">
                <div
                    class="recordapi__header"
                    v-show="!editTestStepActivate"
                    style="margin-top: -10px; margin-left: -10px"
                >
                    <div class="recordapi__header" :style="{ flex: 1 }">
                        <div class="recordapi__header--item">
                            <el-input
                                clearable
                                size="medium"
                                placeholder="请输入接口名称"
                                style="width: 300px"
                                @input="inputVal"
                                :value="search"
                                @keyup.enter.native="getAPIList"
                            ></el-input>
                        </div>
                        <div class="recordapi__header--item">
                            <el-button
                                plain
                                size="medium"
                                icon="el-icon-refresh"
                                @click="resetSearch"
                                >重置</el-button
                            >
                        </div>
                        <div class="recordapi__header--item">
                            <el-dropdown @command="tagChangeHandle">
                                <el-button type="primary" size="medium">
                                    状态
                                    <i
                                        class="el-icon-arrow-down el-icon--right"
                                    ></i>
                                </el-button>
                                <el-dropdown-menu slot="dropdown">
                                    <el-dropdown-item command="1"
                                        >成功</el-dropdown-item
                                    >
                                    <el-dropdown-item command="0"
                                        >未知</el-dropdown-item
                                    >
                                    <el-dropdown-item command="2"
                                        >失败</el-dropdown-item
                                    >
                                    <el-dropdown-item command=""
                                        >所有</el-dropdown-item
                                    >
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div>
                        <div class="recordapi__header--item">
                            <el-select
                                size="medium"
                                v-model="selectUser"
                                placeholder="创建人"
                                filterable
                                :style="{ width: '120px' }"
                            >
                                <el-option
                                    v-for="(item, index) in users"
                                    :key="index"
                                    :label="item.label"
                                    :value="item.value"
                                ></el-option>
                            </el-select>
                        </div>
                    </div>

                    <div class="recordapi__header" :style="{ flex: 1 }">
                        <div class="recordapi__header--item">
                            <el-input
                                size="medium"
                                style="width: 500px"
                                placeholder="请输入测试用例名称"
                                v-model="testName"
                                clearable
                                v-if="testData.length > 0"
                            >
                                <el-select
                                    size="medium"
                                    v-model="testTag"
                                    slot="prepend"
                                    placeholder="请选择"
                                    style="width: 105px"
                                >
                                    <el-option
                                        v-for="value in tagOptions"
                                        :key="value"
                                        :label="value"
                                        :value="value"
                                    ></el-option>
                                </el-select>
                            </el-input>
                        </div>
                        <el-button
                            size="medium"
                            style="margin-left: 10px"
                            v-if="testData.length > 0"
                            type="primary"
                            :loading="loading"
                            @click="handleClickRun"
                            >发送</el-button
                        >

                        <div class="recordapi__header--item">
                            <el-button
                                size="medium"
                                v-if="testData.length > 0"
                                slot="append"
                                type="primary"
                                @click="handleClickSave"
                                :title="
                                    disabledSave
                                        ? '不能修改其他人的用例'
                                        : '保存用例'
                                "
                                :disabled="disabledSave"
                                >保存</el-button
                            >
                        </div>
                    </div>
                </div>

                <div
                    v-show="!editTestStepActivate"
                    style="position: relative; height: 675px; margin-top: 10px;"
                >
                    <div
                        style="height: calc(100% - 50px); overflow-y: auto; overflow-x: hidden;"
                    >
                        <el-row :gutter="20">
                            <el-col :span="12">
                                <div
                                    v-for="(item, index) in apiData.results"
                                    draggable="true"
                                    @dragstart="
                                        currentAPI = JSON.parse(
                                            JSON.stringify(item)
                                        )
                                    "
                                    style="cursor: pointer; margin-top: 10px; overflow: auto"
                                    :key="index"
                                >
                                    <div
                                        class="block"
                                        :class="
                                            `block_${item.method.toLowerCase()}`
                                        "
                                    >
                                        <span
                                            class="block-method block_method_color"
                                            :class="
                                                `block_method_${item.method.toLowerCase()}`
                                            "
                                            >{{
                                                item.method.toUpperCase()
                                            }}</span
                                        >
                                        <div class="block">
                                            <span
                                                class="block-method block_method_color block_method_options"
                                                v-if="item.creator === 'yapi'"
                                                :title="'从YAPI导入的接口'"
                                                >YAPI</span
                                            >
                                        </div>
                                        <span
                                            class="block-method block-api-name-url"
                                            >{{ item.url }}</span
                                        >
                                        <span class="block-api-name-url">{{
                                            item.name
                                        }}</span>
                                        <div>
                                            <span
                                                class="el-icon-s-flag"
                                                v-if="item.cases.length > 0"
                                                :title="
                                                    '接口已被用例引用' +
                                                        item.cases.length +
                                                        '次'
                                                "
                                            ></span>
                                        </div>
                                    </div>
                                </div>
                            </el-col>
                            <el-col :span="12" class="el-col">
                                <el-dialog
                                    v-if="dialogTableVisible"
                                    :visible.sync="dialogTableVisible"
                                    width="70%"
                                >
                                    <report :summary="summary"></report>
                                </el-dialog>

                                <div
                                    @drop="drop($event)"
                                    @dragover="allowDrop($event)"
                                    class="drag-drop-zone"
                                >
                                    <div>
                                        <span
                                            v-if="testData.length === 0"
                                            style="color: red"
                                            >温馨提示：
                                            <br />从左边拖拽API至此区域组成业务用例<br />上下拖动此区域API调整API调用顺序
                                        </span>
                                        <div
                                            v-if="isConfigExist"
                                            class="block block_test"
                                            @mousemove="currentTest = -1"
                                        >
                                            <span
                                                class="block-method block_method_config block_method_color"
                                                >{{
                                                    testData[0].body.method
                                                }}</span
                                            >
                                            <input
                                                class="block-test-name"
                                                v-model="testData[0].body.name"
                                                disabled
                                            />
                                            <el-button
                                                style="position: absolute; right:12px; top:8px"
                                                v-show="currentTest === -1"
                                                type="danger"
                                                icon="el-icon-delete"
                                                title="删除"
                                                circle
                                                size="mini"
                                                @click="testData.splice(0, 1)"
                                            ></el-button>
                                        </div>
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
                                                v-if="
                                                    test.body.method !==
                                                        'config'
                                                "
                                            >
                                                <span
                                                    class="block-method block_method_test block_method_color"
                                                    >Step_{{ index }}</span
                                                >
                                                <input
                                                    class="block-test-name"
                                                    v-model="test.body.name"
                                                />
                                                <el-button
                                                    style="position: absolute; right: 156px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="info"
                                                    icon="el-icon-edit"
                                                    title="编辑"
                                                    circle
                                                    size="mini"
                                                    @click="
                                                        editTestStepActivateHandle
                                                    "
                                                ></el-button>
                                                <el-button
                                                    style="position: absolute; right: 120px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="danger"
                                                    icon="el-icon-document-copy"
                                                    title="复制当前步骤"
                                                    circle
                                                    size="mini"
                                                    @click="
                                                        handleCopyStep(index)
                                                    "
                                                ></el-button>
                                                <el-button
                                                    style="position: absolute; right: 84px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="success"
                                                    icon="el-icon-caret-right"
                                                    title="单个运行"
                                                    circle
                                                    size="mini"
                                                    @click="handleSingleRun"
                                                ></el-button>
                                                <el-button
                                                    style="position: absolute; right: 48px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="primary"
                                                    icon="el-icon-caret-right"
                                                    title="运行开始到当前为止的所有api"
                                                    circle
                                                    size="mini"
                                                    @click="
                                                        handlePartialRun(index)
                                                    "
                                                ></el-button>
                                                <el-button
                                                    circle
                                                    style="position: absolute; right: 12px; top: 8px"
                                                    v-show="
                                                        currentTest === index
                                                    "
                                                    type="danger"
                                                    icon="el-icon-delete"
                                                    title="删除"
                                                    size="mini"
                                                    @click="
                                                        handleSingleDel(index)
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
                            v-show="apiData.count !== 0"
                            background
                            @current-change="handlePageChange"
                            @size-change="handleSizeChange"
                            :current-page.sync="currentPage"
                            :page-sizes="[10, 15, 20]"
                            :page-size="pageSize"
                            :pager-count="5"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="apiData.count"
                            style="margin-top: 5px"
                        ></el-pagination>
                    </div>
                </div>
                <test-body
                    v-if="editTestStepActivate"
                    :host="host"
                    :response="testData[currentTest]"
                    :config="config"
                    :disabledSave="disabledSave"
                    @escEdit="escEditHandle"
                    @getNewBody="handleNewBody"
                ></test-body>
            </el-main>
            <el-button
                v-if="showCancel"
                @click="cancelRequest"
                class="custom-button"
                size="mini"
                >取消</el-button
            >
        </el-container>
    </el-container>
</template>

<script>
import draggable from "vuedraggable";
import TestBody from "./TestBody";
import Report from "@/pages/reports/DebugReport";
import axios from "axios";
import { isEqual } from "lodash";

export default {
    name: "EditTest",
    components: {
        draggable,
        TestBody,
        Report
    },
    props: {
        host: {
            required: true
        },
        config: {
            required: true
        },
        project: {
            required: true
        },
        node: {
            required: true
        },
        testStepResp: {
            required: false
        },
        editBack: Boolean,
        resetEditTestStepActivate: Boolean,
        rigEnv: [String, Number],
        tag: [String, Number],
        search: [String, Number],
        addTestActivate: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            originalData: [],
            tagOptions: {
                1: "冒烟用例",
                2: "集成用例",
                3: "监控用例",
                4: "核心用例"
            },
            isSuperuser: this.$store.state.is_superuser,
            userId: this.$store.state.id,
            disabledSave: true,
            showCancel: false,
            loading: false,
            dialogTableVisible: false,
            editTestStepActivate: false,
            currentPage: 1,
            pageSize: 10,
            length: 0,
            testId: "",
            testName: "",
            relation: "",
            testTag: "集成用例",
            currentTest: "",
            currentNode: "",
            currentAPI: "",
            data: "",
            filterText: "",
            expand: "&#xe65f;",
            dataTree: [],
            summary: {},
            apiData: {
                count: 0,
                results: []
            },
            testData: [],
            selectUser: this.$store.state.name,
            users: [],
            searchDebounce: null
        };
    },
    computed: {
        isConfigExist: {
            get() {
                return (
                    this.testData.length > 0 &&
                    this.testData[0].body.method === "config" &&
                    this.testData[0].body.name !== "请选择"
                );
            }
        }
    },
    watch: {
        search() {
            this.debouncedGetAPIList();
        },
        selectUser() {
            this.debouncedGetAPIList();
        },
        config() {
            const temp = { body: { name: this.config, method: "config" } };
            if (
                (this.testData.length === 0 ||
                    this.testData[0].body.method !== "config") &&
                this.config !== "请选择"
            ) {
                this.testData.splice(0, 0, temp);
            } else {
                if (this.config !== "请选择") {
                    this.testData.splice(0, 1, temp);
                }
            }
        },
        editBack() {
            this.handleResetStatus();
            if (this.editBack) {
                this.testId = "";
                this.testName = "";
                this.testData = [];
            }
            this.editTestStepActivate = false;
        },
        resetEditTestStepActivate() {
            this.editTestStepActivate = false;
        },
        filterText(val) {
            this.$refs.tree.filter(val);
        },
        testStepResp: {
            deep: true,
            handler() {
                this.handleSavePermission();
                try {
                    this.testName = this.testStepResp.case.name;
                    this.testId = this.testStepResp.case.id;
                    this.testTag = this.testStepResp.case.tag;
                    this.relation = this.testStepResp.case.relation;
                    this.testData = JSON.parse(
                        JSON.stringify(this.testStepResp.step)
                    );
                } catch (e) {
                    this.testName = "";
                    this.testId = "";
                    this.testTag = "集成用例";
                    this.testData = [];
                }
                this.setOriginalData();
            }
        },
        testName() {
            this.checkForChanges();
        },
        testTag() {
            this.checkForChanges();
        },
        testData: {
            deep: true,
            handler() {
                this.checkForChanges();
            }
        }
    },
    methods: {
        escEditHandle() {
            this.editTestStepActivate = false;
            this.$emit("showListBtn", true);
        },
        editTestStepActivateHandle() {
            this.editTestStepActivate = true;
            this.$emit("showListBtn", false);
        },
        checkForChanges() {
            const currentData = {
                testName: this.testName,
                testTag: this.testTag,
                testSteps: this.testData
            };
            const hasChanged = !isEqual(this.originalData, currentData);
            this.$emit("dataChanged", hasChanged);
        },
        setOriginalData() {
            if (this.testStepResp && this.testStepResp.step) {
                this.originalData = {
                    testName: this.testStepResp.case.name,
                    testTag: this.testStepResp.case.tag,
                    testSteps: JSON.parse(
                        JSON.stringify(this.testStepResp.step)
                    )
                };
            } else {
                this.originalData = {
                    testName: this.testName,
                    testTag: this.testTag,
                    testSteps: JSON.parse(JSON.stringify(this.testData))
                };
            }
        },
        debouncedGetAPIList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.currentPage = 1;
                this.getAPIList();
            }, 300);
        },
        handleSavePermission() {
            // 新增用例时，所有人都能保存
            if (this.addTestActivate === false) {
                this.disabledSave = false;
            }
            // 用例创建人和超级管理员可以编辑并保存用例, 其他人只能打开用例，无法保存
            if (this.testStepResp && this.testStepResp.case) {
                this.disabledSave = !(
                    this.isSuperuser ||
                    this.testStepResp.case.creator === this.userId
                );
            }
        },
        inputVal(val) {
            this.$emit("update:search", val);
        },
        handleNewBody(body, newBody) {
            this.editTestStepActivate = false;
            const source_api_id = this.testData[this.currentTest].source_api_id;
            const step = this.testData[this.currentTest].case;
            const id = this.testData[this.currentTest].id;
            this.testData[this.currentTest] = {
                body: body,
                newBody: newBody,
                case: step,
                id: id,
                source_api_id: source_api_id
            };
            // 编辑用例步骤内容时，也调用接口保存
            this.handleClickSave(false, true);
        },
        rigEnvChangeHandle(command) {
            this.$emit("update:rigEnv", command);
            this.getAPIList();
        },
        handleClickSave(addTestFinish = true, isEditTestStep = false) {
            if (this.validateData()) {
                if (this.testId === "") {
                    this.addTestSuite(addTestFinish, isEditTestStep);
                } else {
                    this.updateTestSuite(addTestFinish, false, isEditTestStep);
                }
            }
        },
        cancelToken() {
            this.showCancel = true;

            // 创建 cancel token
            this.cancelTokenSource = axios.CancelToken.source();

            // 设置一个定时器，2分钟后执行
            return setTimeout(() => {
                this.apiRunning = false;
                this.cancelTokenSource.cancel("Request timed out");
            }, 120000);
        },
        cancelRequest() {
            this.loading = false; // 关闭Loading
            this.showCancel = false; // 隐藏‘取消请求’按钮
            this.cancelTokenSource.cancel("User cancelled the request"); // 取消请求
        },
        // 全部运行
        handleClickRun() {
            if (this.validateData()) {
                this.loading = true;
                const timeout = this.cancelToken();
                this.$api
                    .runSingleTestSuite(
                        {
                            host: this.host,
                            name: this.testName,
                            body: this.testData,
                            project: this.project
                        },
                        this.cancelTokenSource.token
                    )
                    .then(resp => {
                        clearTimeout(timeout); // 清除定时器
                        this.loading = false;
                        this.summary = resp;
                        this.dialogTableVisible = true;
                        this.showCancel = false; // 请求成功完成，隐藏‘取消请求’按钮
                    })
                    .catch(err => {
                        clearTimeout(timeout); // 清除定时器
                        if (!axios.isCancel(err)) {
                            // 如果错误不是由取消请求引起的，则处理错误
                            this.loading = false;
                            this.$message.error(err);
                        }
                        this.showCancel = false; // 请求失败，隐藏‘取消请求’按钮
                    });
            }
        },
        // 运行开始到当前位置的所有api
        handlePartialRun(index) {
            if (this.validateData()) {
                this.loading = true;
                const timeout = this.cancelToken();
                this.$api
                    .runSingleTestSuite(
                        {
                            host: this.host,
                            name: this.testName,
                            body: this.testData.slice(0, index + 1),
                            project: this.project
                        },
                        this.cancelTokenSource.token
                    )
                    .then(resp => {
                        clearTimeout(timeout); // 清除定时器
                        this.loading = false;
                        this.summary = resp;
                        this.dialogTableVisible = true;
                        this.showCancel = false;
                    })
                    .catch(err => {
                        clearTimeout(timeout);
                        if (!axios.isCancel(err)) {
                            // 如果错误不是由取消请求引起的，则处理错误
                            this.loading = false;
                            this.$message.error(err);
                        }
                        this.showCancel = false;
                    });
            }
        },
        // 单个运行
        handleSingleRun() {
            let config = null;
            this.loading = true;
            const timeout = this.cancelToken();
            if (
                this.testData.length > 0 &&
                this.testData[0].body.method === "config" &&
                this.testData[0].body.name !== "请选择"
            ) {
                config = this.testData[0].body;
            } else {
                this.$notify.warning({
                    title: "提示",
                    message: "测试用例必须包含配置",
                    duration: this.$store.state.duration
                });
                this.loading = false;
                return;
            }
            this.$api
                .runSingleTest(
                    {
                        host: this.host,
                        config: config,
                        body: this.testData[this.currentTest],
                        project: this.project
                    },
                    this.cancelTokenSource.token
                )
                .then(resp => {
                    clearTimeout(timeout); // 清除定时器
                    this.loading = false;
                    this.summary = resp;
                    this.dialogTableVisible = true;
                    this.showCancel = false;
                })
                .catch(err => {
                    clearTimeout(timeout);
                    if (!axios.isCancel(err)) {
                        // 如果错误不是由取消请求引起的，则处理错误
                        this.loading = false;
                        this.$message.error(err);
                    }
                    this.showCancel = false;
                });
        },
        failure(resp) {
            this.$notify.error({
                title: "失败",
                message: resp["msg"],
                duration: this.$store.state.duration
            });
        },
        handleSingleDel(index) {
            this.testData.splice(index, 1);
            if (
                this.testData.length === 1 &&
                this.testData[0].body.name === "请选择"
            ) {
                this.testData.splice(0, 1);
            }
        },
        handlePageChange() {
            this.$api
                .getAPIPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: this.pageSize,
                        node: this.currentNode,
                        project: this.project,
                        tag: this.tag,
                        rigEnv: this.rigEnv,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.apiData = resp.data;
                });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.apiData.count / newSize);
            if (this.currentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.currentPage = maxPage;
            }
            this.$api
                .getAPIPaginationByPage({
                    params: {
                        page: this.currentPage,
                        size: newSize,
                        node: this.currentNode,
                        project: this.project,
                        tag: this.tag,
                        rigEnv: this.rigEnv,
                        search: this.search
                    }
                })
                .then(resp => {
                    this.apiData = resp.data;
                });
        },
        // 接口状态搜索
        tagChangeHandle(command) {
            this.$emit("update:tag", command);
            this.$nextTick(() => {
                this.$api
                    .apiList({
                        params: {
                            page: this.currentPage,
                            size: this.pageSize,
                            node: this.currentNode,
                            project: this.project,
                            tag: this.tag,
                            rigEnv: this.rigEnv,
                            search: this.search,
                            creator: this.selectUser
                        }
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.apiData = resp.data;
                        } else {
                            this.$message({
                                type: "error",
                                message: resp.msg
                            });
                        }
                    });
            });
        },
        handleResetStatus() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.selectUser = this.$store.state.name;
            this.currentNode = "";
            this.$emit("update:search", "");
            this.$emit("update:tag", "");
            this.$emit("update:rigEnv", "");
        },
        resetSearch() {
            this.handleResetStatus();
            this.getAPIList();
        },
        getAPITree() {
            this.$api
                .getTree(this.$route.params.id, {
                    params: {
                        type: 1
                    }
                })
                .then(resp => {
                    this.dataTree = resp["tree"];
                });
        },
        handleNodeClick(node, data) {
            // 点击子目录把页码重置设置为1
            this.currentPage = 1;
            this.currentNode = node.id;
            this.data = data;
            this.getAPIList();
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        dragEnd() {
            if (this.testData.length > this.length) {
                this.testData.splice(this.length, 1);
            }
        },
        drop(event) {
            event.preventDefault();
            // 创建用例时, 默认加上config
            if (this.testData.length === 0) {
                this.testData.push({
                    body: { name: this.config, method: "config" }
                });
            }
            if (this.currentAPI) {
                this.testData.push(this.currentAPI);
                this.currentAPI = "";
            }
        },
        allowDrop(event) {
            event.preventDefault();
        },
        getUserList() {
            this.$api.getUserList().then(resp => {
                for (let i = 0; i < resp.length; i++) {
                    this.users.push({
                        label: resp[i].name,
                        value: resp[i].name
                    });
                }
                // 在数组第一个位置插入值
                this.users.unshift({ label: "所有人", value: "" });
            });
        },
        validateData() {
            if (this.testName === "" || this.testName.length > 100) {
                this.$notify.warning({
                    title: "提示",
                    message: "用例名称必填, 不能超过100个字符",
                    duration: this.$store.state.duration
                });
                return false;
            }

            if (this.testData.length === 0) {
                this.$notify.warning({
                    title: "提示",
                    message: "测试用例至少包含一个接口",
                    duration: this.$store.state.duration
                });
                return false;
            }

            if (
                this.testData[0].body.method === "config" &&
                this.testData.length === 1
            ) {
                this.$notify.warning({
                    title: "提示",
                    message: "测试用例至少包含一个接口",
                    duration: this.$store.state.duration
                });
                return false;
            }

            if (
                this.testData[0].body.name === "请选择" ||
                this.testData[0].body.method !== "config"
            ) {
                this.$notify.warning({
                    title: "提示",
                    message: "测试用例必须包含配置",
                    duration: this.$store.state.duration
                });
                return false;
            }
            return true;
        },
        addTestSuite(addTestFinish, isEditTestStep) {
            let len = this.testData.length;
            if (this.testData[0].body.method === "config") {
                len -= 1;
            }
            this.$api
                .addTestCase({
                    length: len,
                    project: this.project,
                    relation: this.node,
                    name: this.testName,
                    body: this.testData,
                    tag: this.testTag
                })
                .then(resp => {
                    if (resp.success) {
                        this.testId = resp.test_id;

                        if (addTestFinish) {
                            this.$emit("addSuccess");
                        }

                        if (isEditTestStep) {
                            this.$emit("showListBtn", true);
                        } else {
                            this.handleResetStatus(); // 重置搜索条件
                            this.$emit("showListBtn", false);
                        }
                        this.$message.success(resp.msg);
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
        },
        updateTestSuite(addTestFinish, refresh = false, isEditTestStep) {
            let len = this.testData.length;
            if (this.testData[0].body.method === "config") {
                len -= 1;
            }

            this.$api
                .updateTestCase(this.testId, {
                    length: len,
                    name: this.testName,
                    tag: this.testTag,
                    body: this.testData,
                    project: this.project
                })
                .then(resp => {
                    // 刷新用例步骤
                    // 注意需要等到用例步骤刷新完毕后，再刷新用例列表
                    if (refresh) {
                        this.refreshStep();
                    }

                    if (resp.success) {
                        if (addTestFinish) {
                            this.$emit("addSuccess");
                        }

                        if (isEditTestStep) {
                            this.$emit("showListBtn", true);
                        } else {
                            this.handleResetStatus(); // 重置搜索条件
                            this.$emit("showListBtn", false);
                        }
                        this.$message.success(resp.msg);
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
        },
        refreshStep() {
            this.$api.editTest(this.testId).then(resp => {
                this.testData = JSON.parse(JSON.stringify(resp.step));
            });
        },
        getAPIList() {
            this.$nextTick(() => {
                this.$api
                    .apiList({
                        params: {
                            page: this.currentPage,
                            size: this.pageSize,
                            node: this.currentNode,
                            project: this.project,
                            search: this.search,
                            rigEnv: this.rigEnv,
                            tag: this.tag,
                            creator: this.selectUser
                        }
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.apiData = resp.data;
                        } else {
                            this.$message({
                                type: "error",
                                message: resp.msg
                            });
                        }
                    });
            });
        },
        handleCopyStep(index) {
            let copyStepObj = JSON.parse(JSON.stringify(this.testData[index]));
            copyStepObj.is_copy = true;
            this.testData.splice(index + 1, 0, copyStepObj);
            this.updateTestSuite(false, true);
        }
    },
    mounted() {
        this.getAPITree();
        this.getAPIList();
        this.getUserList();
        this.setOriginalData();
    }
};
</script>

<style scoped>
.el-col {
    min-height: 1px;
}

.test-list {
    height: 750px;
}

.block_test {
    margin-top: 10px;
    border: 1px solid #49cc90;
    background-color: rgba(236, 248, 238, 0.4);
}

.block_method_test {
    background-color: darkcyan;
}

.block_method_config {
    background-color: red;
}

.block-test-name {
    /*修改用例中API名字显示不全*/
    width: 450px;
    /*超过宽度自动变成...*/
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    padding-left: 10px;
    font-family: Open Sans, sans-serif;
    color: #3b4151;
    border: none;
    outline: none;
    background: rgba(236, 248, 238, 0.4);
}

.recordapi__header {
    display: flex;
    align-items: center;
}

.recordapi__header--item {
    display: flex;
    margin-left: 10px;
}

.custom-button {
    position: absolute; /* 使用绝对定位 */
    top: calc(50% + 40px); /* 从容器的顶部开始，向下移动50% + 20px */
    left: 50%; /* 从容器的左边开始，向右移动50% */
    transform: translate(-50%, -50%); /* 使用 transform 居中按钮 */
    z-index: 2000; /* 确保按钮在 Loading 动画之上 */
}

.loading-container {
    position: relative; /* 添加这个让子元素可以相对于此容器定位 */
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

.drag-drop-zone {
    min-height: 200px;
}
</style>
