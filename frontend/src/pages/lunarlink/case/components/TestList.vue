<template>
    <el-container>
        <el-header style="padding-top: 10px; height: 50px;">
            <div class="case__header">
                <div class="case__header--item">
                    <el-input
                        :placeholder="placeholderText"
                        clearable
                        size="small"
                        v-model="search"
                        class="input-with-select"
                        style="width: 300px"
                    >
                        <el-select
                            v-model="searchType"
                            slot="prepend"
                            placeholder="用例"
                            @change="searchTypeChangeHandle"
                        >
                            <el-option label="用例" value="1"></el-option>
                            <el-option label="API" value="2"></el-option>
                        </el-select>
                    </el-input>
                </div>

                <div class="case__header--item">
                    <el-date-picker
                        v-model="dateRange"
                        type="daterange"
                        size="small"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        value-format="yyyy-MM-dd"
                        style="width: 250px"
                    >
                    </el-date-picker>
                </div>

                <div class="case__header--item">
                    <el-select
                        v-model="creator"
                        placeholder="请选择创建人"
                        size="small"
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

                <div class="case__header--item">
                    <el-dropdown @command="caseTypeChangeHandle" size="small">
                        <el-button type="primary" size="small">
                            类型
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="1"
                                >冒烟用例</el-dropdown-item
                            >
                            <el-dropdown-item command="2"
                                >集成用例</el-dropdown-item
                            >
                            <el-dropdown-item command="3"
                                >监控用例</el-dropdown-item
                            >
                            <el-dropdown-item command="4"
                                >核心用例</el-dropdown-item
                            >
                            <el-dropdown-item command="">所有</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>

                <div class="case__header--item">
                    <el-button
                        plain
                        @click="resetSearch"
                        size="small"
                        icon="el-icon-refresh"
                        >重置</el-button
                    >
                </div>
            </div>
        </el-header>

        <el-container>
            <el-main style="padding: 0; margin-left: 10px;">
                <el-dialog
                    v-if="dialogTableVisible"
                    :visible.sync="dialogTableVisible"
                    width="70%"
                    :modal-append-to-body="false"
                >
                    <report :summary="summary"></report>
                </el-dialog>

                <el-dialog
                    width="45%"
                    title="Run Case"
                    :visible.sync="dialogTreeRunCaseVisible"
                    :close-on-click-modal="false"
                    :modal-append-to-body="false"
                    @close="onCloseRunCase"
                    @open="onOpenRunCase"
                >
                    <div style="max-width: 100%;">
                        <div>
                            <el-row :gutter="10">
                                <el-col :span="8">
                                    <span>&nbsp配置</span>
                                    <el-select
                                        placeholder="请选择"
                                        size="medium"
                                        v-model="currentConfigId"
                                        style="width: 200px"
                                    >
                                        <el-option
                                            v-for="item in configOptions"
                                            :key="item.id"
                                            :label="item.name"
                                            :value="item.id"
                                        ></el-option>
                                    </el-select>
                                </el-col>
                                <el-col :span="6">
                                    <el-switch
                                        style="margin-top: 10px"
                                        v-model="async_"
                                        active-color="#13ce66"
                                        inactive-color="#ff4949"
                                        active-text="异步执行"
                                        inactive-text="同步执行"
                                    ></el-switch>
                                </el-col>
                                <el-col :span="8">
                                    <el-input
                                        v-show="async_"
                                        clearable
                                        placeholder="请输入测试报告"
                                        v-model="reportName"
                                        :disabled="false"
                                    ></el-input>
                                </el-col>
                            </el-row>
                        </div>
                        <div style="margin-top: 20px; max-width: 100%;">
                            <el-input
                                placeholder="请输入关键字进行过滤"
                                v-model="filterText"
                                size="medium"
                                clearable
                                prefix-icon="el-icon-search"
                            ></el-input>
                            <el-tree
                                :filter-node-method="filterNode"
                                :data="dataTree"
                                show-checkbox
                                node-key="id"
                                :expand-on-click-node="false"
                                check-on-click-node
                                :check-strictly="true"
                                :highlight-current="true"
                                ref="run_tree"
                                style="max-width: 100%;"
                            >
                                <span
                                    class="custom-tree-node"
                                    slot-scope="{ node, data }"
                                    style="display: flex; flex-direction: row; min-width: 0;"
                                >
                                    <span
                                        style="overflow: hidden; text-overflow:ellipsis; white-space: nowrap; flex: 0 1 auto;"
                                    >
                                        <i
                                            v-if="node.childNodes.length > 0"
                                            class="el-icon-folder-opened"
                                        ></i>
                                        <i v-else class="el-icon-folder"></i
                                        >&nbsp;&nbsp;{{ node.label
                                        }}<el-badge
                                            :value="data.data_count"
                                            :max="99"
                                            class="badge-item"
                                            type="primary"
                                        ></el-badge>
                                    </span>
                                </span>
                            </el-tree>
                        </div>
                    </div>
                    <span
                        slot="footer"
                        class="dialog-footer"
                        style="display: flex; justify-content: flex-end"
                    >
                        <el-button @click="dialogTreeRunCaseVisible = false"
                            >取 消</el-button
                        >
                        <el-button type="primary" @click="runTreeCase"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>

                <el-dialog
                    title="移动用例"
                    :visible.sync="dialogTreeMoveCaseVisible"
                    :before-close="handleBeforeClose"
                    :close-on-click-modal="false"
                    :modal-append-to-body="false"
                    :style="{ 'text-align': 'center' }"
                    width="30%"
                >
                    <el-form
                        :model="caseDirForm"
                        :rules="caseDirRules"
                        ref="caseDirForm"
                        label-width="100px"
                    >
                        <el-form-item label="用例目录" prop="caseDir">
                            <el-select
                                v-model="selectedCaseNodeLabel"
                                value-key="id"
                                placeholder="请选择接口目录"
                                :style="{ width: '100%' }"
                                ref="selectCaseNode"
                            >
                                <el-option
                                    :value="selectCaseOptionValue"
                                    class="tree-select-option-item"
                                >
                                    <el-tree
                                        :data="dataTree"
                                        :expand-on-click-node="false"
                                        :check-strictly="true"
                                        @node-click="handleCaseNodeClick"
                                        highlight-current
                                        node-key="id"
                                        check-on-click-node
                                        style="max-width: 100%;"
                                    >
                                        <span
                                            class="custom-tree-node"
                                            slot-scope="{ node, data }"
                                            style="display: flex; flex-direction: row; min-width: 0;"
                                        >
                                            <span class="el-tree-span">
                                                <i
                                                    v-if="
                                                        node.childNodes.length >
                                                            0
                                                    "
                                                    class="el-icon-folder-opened"
                                                ></i>
                                                <i
                                                    v-else
                                                    class="el-icon-folder"
                                                ></i
                                                >&nbsp;&nbsp;{{ node.label
                                                }}<el-badge
                                                    :value="data.data_count"
                                                    :max="99"
                                                    class="badge-item"
                                                    type="primary"
                                                ></el-badge>
                                            </span>
                                        </span>
                                    </el-tree>
                                </el-option>
                            </el-select>
                        </el-form-item>
                    </el-form>
                    <span
                        slot="footer"
                        class="dialog-footer"
                        style="display: flex; justify-content: flex-end"
                    >
                        <el-button @click="resetForm('caseDirForm')"
                            >取 消</el-button
                        >
                        <el-button
                            type="primary"
                            @click="moveCase('caseDirForm')"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>
                <div class="loading-container">
                    <div class="test-body-table" v-loading="tableLoading">
                        <el-table
                            highlight-current-row
                            v-loading="caseRunning"
                            ref="multipleTable"
                            :data="testData.results"
                            :show-header="testData.count !== 0"
                            stripe
                            height="calc(100%)"
                            @cell-mouse-enter="cellMouseEnter"
                            @cell-mouse-leave="cellMouseLeave"
                            @selection-change="handleSelectionChange"
                        >
                            <el-table-column
                                class="no-padding-left"
                                type="selection"
                                width="42"
                            ></el-table-column>

                            <el-table-column width="25">
                                <template v-slot="scope">
                                    <el-dropdown
                                        @command="dropdownMenuChangeHandle"
                                    >
                                        <span
                                            ><i class="el-icon-more"></i
                                        ></span>
                                        <el-dropdown-menu slot="dropdown">
                                            <el-dropdown-item
                                                disabled
                                                style="background-color: #e2e2e2"
                                                >{{
                                                    selectTest.length
                                                }}
                                                条更新为</el-dropdown-item
                                            >
                                            <el-dropdown-item
                                                :disabled="
                                                    selectTest.length === 0
                                                "
                                                command="core"
                                                >核心用例</el-dropdown-item
                                            >
                                            <el-dropdown-item
                                                :disabled="
                                                    selectTest.length === 0
                                                "
                                                command="integrated"
                                                >集成用例</el-dropdown-item
                                            >
                                            <el-dropdown-item
                                                :disabled="
                                                    selectTest.length === 0
                                                "
                                                command="smoke"
                                                >冒烟用例</el-dropdown-item
                                            >
                                            <el-dropdown-item
                                                :disabled="
                                                    selectTest.length === 0
                                                "
                                                command="monitor"
                                                >监控用例</el-dropdown-item
                                            >
                                        </el-dropdown-menu>
                                    </el-dropdown>
                                </template>
                            </el-table-column>

                            <el-table-column label="用例名称" width="250">
                                <template v-slot="scope">
                                    <div
                                        :title="scope.row.name"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{ scope.row.name }}
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="步骤" width="80">
                                <template slot-scope="scope">
                                    <el-tag>{{ scope.row.length }}</el-tag>
                                </template>
                            </el-table-column>

                            <el-table-column label="任务关联" width="100">
                                <template v-slot="scope">
                                    <div>
                                        <div
                                            v-if="scope.row.tasks.length > 0"
                                            :title="
                                                '已关联定时任务: ' +
                                                    scope.row.tasks
                                                        .map(task => task.name)
                                                        .join(', ')
                                            "
                                            style="display: inline-flex; align-items: center;"
                                        >
                                            <i
                                                class="el-icon-success"
                                                style="color: #13ce66; margin-right: 5px;"
                                            ></i>
                                            <span>已关联</span>
                                        </div>
                                        <div
                                            v-if="scope.row.tasks.length === 0"
                                            style="display: inline-flex; align-items: center;"
                                        >
                                            <i
                                                class="el-icon-error"
                                                style="color: red; margin-right: 5px;"
                                            ></i>
                                            <span>未关联</span>
                                        </div>
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="用例类型" width="100">
                                <template v-slot="scope">
                                    <el-tag
                                        v-if="scope.row.tag === '冒烟用例'"
                                        >{{ scope.row.tag }}</el-tag
                                    >
                                    <el-tag
                                        v-if="scope.row.tag === '集成用例'"
                                        type="info"
                                        >{{ scope.row.tag }}</el-tag
                                    >
                                    <el-tag
                                        v-if="scope.row.tag === '监控用例'"
                                        type="danger"
                                        >{{ scope.row.tag }}</el-tag
                                    >
                                    <el-tag
                                        v-if="scope.row.tag === '核心用例'"
                                        type="success"
                                        >{{ scope.row.tag }}</el-tag
                                    >
                                </template>
                            </el-table-column>

                            <el-table-column label="创建人" width="100">
                                <template v-slot="scope">
                                    <div
                                        :title="scope.row.creator_name"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{ scope.row.creator_name }}
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="更新人" width="100">
                                <template v-slot="scope">
                                    <div
                                        :title="scope.row.updater_name"
                                        style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                                    >
                                        {{
                                            scope.row.updater_name
                                                ? scope.row.updater_name
                                                : "-"
                                        }}
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="创建时间" width="120">
                                <template v-slot="scope">
                                    <div>
                                        {{
                                            scope.row.create_time
                                                | datetimeFormat("MM-DD hh:mm")
                                        }}
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="更新时间" width="120">
                                <template v-slot="scope">
                                    <div>
                                        {{
                                            scope.row.update_time
                                                | datetimeFormat("MM-DD hh:mm")
                                        }}
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column label="用例操作">
                                <template v-slot="scope">
                                    <el-row v-show="currentRow === scope.row">
                                        <div
                                            style="display: flex; align-items: center;"
                                        >
                                            <el-button
                                                type="info"
                                                icon="el-icon-edit"
                                                circle
                                                size="mini"
                                                title="编辑"
                                                @click="
                                                    handleEditTest(scope.row.id)
                                                "
                                            ></el-button>
                                            <el-button
                                                type="primary"
                                                icon="el-icon-caret-right"
                                                circle
                                                size="mini"
                                                title="同步运行用例"
                                                @click="
                                                    handleRunTest(
                                                        scope.row.id,
                                                        scope.row.name
                                                    )
                                                "
                                            ></el-button>
                                            <el-button
                                                type="primary"
                                                icon="el-icon-video-play"
                                                circle
                                                size="mini"
                                                title="异步运行用例"
                                                @click="
                                                    handleAsyncRunTest(
                                                        scope.row.id,
                                                        scope.row.name
                                                    )
                                                "
                                            ></el-button>

                                            <el-popover
                                                style="margin-left: 10px"
                                                trigger="hover"
                                            >
                                                <div
                                                    style="display: flex; text-align: center"
                                                >
                                                    <el-button
                                                        type="success"
                                                        icon="el-icon-document-copy"
                                                        circle
                                                        size="mini"
                                                        title="复制用例"
                                                        @click="
                                                            handleCopyTest(
                                                                scope.row.id,
                                                                scope.row.name
                                                            )
                                                        "
                                                    ></el-button>

                                                    <el-button
                                                        type="danger"
                                                        icon="el-icon-delete"
                                                        :title="
                                                            userId ===
                                                                scope.row
                                                                    .creator ||
                                                            isSuperuser
                                                                ? '删除'
                                                                : '只有用例创建者才能删除'
                                                        "
                                                        :disabled="
                                                            userId !==
                                                                scope.row
                                                                    .creator &&
                                                                !isSuperuser
                                                        "
                                                        circle
                                                        size="mini"
                                                        @click="
                                                            handleDelTest(
                                                                scope.row.id
                                                            )
                                                        "
                                                    ></el-button>

                                                    <el-button
                                                        type="warning"
                                                        icon="el-icon-refresh"
                                                        :title="
                                                            userId !==
                                                                scope.row
                                                                    .creator &&
                                                            !isSuperuser
                                                                ? '只有用例创建者才能同步'
                                                                : '从API同步用例步骤'
                                                        "
                                                        :disabled="
                                                            userId !==
                                                                scope.row
                                                                    .creator &&
                                                                !isSuperuser
                                                        "
                                                        circle
                                                        size="mini"
                                                        @click="
                                                            handleSyncCaseStep(
                                                                scope.row.id
                                                            )
                                                        "
                                                    ></el-button>
                                                </div>
                                                <el-button
                                                    icon="el-icon-more"
                                                    title="更多"
                                                    circle
                                                    size="mini"
                                                    slot="reference"
                                                ></el-button>
                                            </el-popover>
                                        </div>
                                    </el-row>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination-container">
                            <el-pagination
                                @current-change="handleCurrentChange"
                                @size-change="handleSizeChange"
                                :current-page.sync="localCurrentPage"
                                :page-sizes="[10, 20, 30, 40]"
                                :page-size="localPageSize"
                                :pager-count="5"
                                v-show="testData.count > 0"
                                :total="testData.count"
                                layout="total, sizes, prev, pager, next, jumper"
                                background
                            ></el-pagination>
                        </div>
                        <el-button
                            v-if="showCancel"
                            @click="cancelRequest"
                            class="custom-button"
                            size="mini"
                            >取消</el-button
                        >
                    </div>
                </div>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import Report from "@/pages/reports/DebugReport";
import axios from "axios";
export default {
    name: "TestList",
    components: {
        Report
    },
    props: {
        run: Boolean,
        // 父组件修改move状态，子组件监听move，调用getTree('move')修改dialogTreeMoveCaseVisible状态，激活移动用例弹窗
        move: Boolean,
        back: Boolean,
        project: {
            required: true
        },
        host: {
            required: true
        },
        pNode: {
            required: false
        },
        pageSize: Number,
        currentPage: Number,
        del: Boolean,
        isSelectCase: Boolean
    },
    data() {
        return {
            creator: this.$store.state.name,
            creatorOptions: [],
            dateRange: [],
            tooltipShown: [],
            isSuperuser: this.$store.state.is_superuser,
            userId: this.$store.state.id,
            search: "",
            reportName: "",
            async_: false,
            filterText: "",
            expand: "&#xe65f",
            dialogTreeRunCaseVisible: false,
            dataTree: [],
            selectedCaseNodeLabel: "",
            selectCaseOptionValue: undefined,
            tableLoading: false, // 用于控制表格数据加载的状态
            caseRunning: false, // 用于控制用例运行请求的状态
            showCancel: false, // 用于控制取消按钮的显示
            cancelTokenSource: null, // 取消请求
            dialogTableVisible: false,
            dialogTreeMoveCaseVisible: false,
            selectTest: [],
            summary: {},
            currentRow: "",
            testData: {
                count: 0,
                results: []
            },
            caseDirForm: {
                caseDir: ""
            },
            node: "",
            caseType: "",
            searchType: "1", // 1：用例名称搜索 2：api名称或者api url搜索
            currentConfigId: "",
            configOptions: [],
            localCurrentPage: this.currentPage || 1,
            localPageSize: this.pageSize || 10,
            searchDebounce: null,
            caseDirRules: {
                caseDir: [
                    {
                        required: true,
                        message: "请选择用例目录",
                        trigger: "change"
                    }
                ]
            }
        };
    },
    computed: {
        placeholderText() {
            return this.searchType === "1"
                ? "请输入用例名称"
                : "请输入API名称或路径";
        }
    },
    watch: {
        search() {
            this.debouncedGetTestList();
        },
        creator() {
            this.debouncedGetTestList();
        },
        dateRange() {
            this.debouncedGetTestList();
        },
        currentPage(newValue) {
            this.localCurrentPage = newValue;
        },
        pageSize(newValue) {
            this.localPageSize = newValue;
        },
        filterText(val) {
            this.$refs.tree.filter(val);
        },
        run() {
            this.async_ = false;
            this.reportName = "";
            this.getTree("run");
        },
        move() {
            this.getTree("move");
        },
        pNode() {
            this.node = this.pNode;
            this.search = "";
            this.searchType = "1";
            this.debouncedGetTestList();
        },
        back() {
            this.debouncedGetTestList();
        },
        del() {
            if (this.selectTest.length !== 0) {
                this.$confirm("此操作将永久删除测试用例, 是否继续?", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                }).then(() => {
                    this.$api
                        .delAllTest({ data: this.selectTest })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success(resp.msg);
                                this.$emit("refreshTree");
                                this.getTestList();
                            } else {
                                this.$message.error(resp.msg);
                            }
                        });
                });
            } else {
                this.$notify.warning({
                    title: "提示",
                    message: "请至少选一个用例",
                    duration: this.$store.state.duration
                });
            }
        }
    },
    methods: {
        debouncedGetTestList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.localCurrentPage = 1;
                this.getTestList();
            }, 300);
        },
        handleCaseNodeClick(node) {
            this.caseDirForm.caseDir = node.id;
            this.selectedCaseNodeLabel = node.label;
            this.$refs.selectCaseNode.toggleMenu();
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
        },
        showTooltip(index) {
            this.$set(this.tooltipShown, index, true);
        },
        getTree(showType) {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 2 } })
                .then(resp => {
                    this.dataTree = resp.tree;
                    // run是批量运行case弹窗, 其他是批量更新case relation弹窗
                    if (showType === "run") {
                        this.dialogTreeRunCaseVisible = true;
                    } else {
                        this.dialogTreeMoveCaseVisible = true;
                    }
                });
        },
        getTestList() {
            this.tableLoading = true;
            this.$nextTick(() => {
                this.$api
                    .testList({
                        params: {
                            page: this.localCurrentPage,
                            size: this.localPageSize,
                            node: this.node,
                            project: this.project,
                            search: this.search,
                            searchType: this.searchType,
                            caseType: this.caseType,
                            creator: this.creator,
                            start_time: (this.dateRange || [])[0],
                            end_time: (this.dateRange || [])[1]
                        }
                    })
                    .then(resp => {
                        this.testData = resp;
                        this.tableLoading = false;
                    });
            });
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        runTreeCase() {
            const relation = this.$refs.run_tree.getCheckedKeys();
            if (relation.length === 0) {
                this.$notify.error({
                    title: "提示",
                    message: "请至少选择一个目录",
                    duration: 2000
                });
            } else {
                this.$api
                    .runSuiteTree({
                        host: this.host,
                        project: this.project,
                        relation: relation,
                        async: this.async_,
                        name: this.reportName,
                        config_id: this.currentConfigId
                    })
                    .then(resp => {
                        if (resp.hasOwnProperty("status")) {
                            this.$message.info({
                                message: resp.msg,
                                duration: 2000
                            });
                        } else {
                            this.summary = resp;
                            this.dialogTableVisible = true;
                        }
                        this.dialogTreeRunCaseVisible = false;
                    });
            }
        },
        moveCase(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.$api
                        .moveCase({
                            project: this.project,
                            relation: this.caseDirForm.caseDir,
                            case: this.selectTest
                        })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success("用例移动成功");
                                // this.dialogTreeMoveCaseVisible = false;
                                this.$emit("refreshTree");
                                this.getTestList();
                            } else {
                                this.$message.error({
                                    message: resp.msg,
                                    duration: 2000
                                });
                            }
                            this.resetForm(formName);
                        });
                }
            });
        },
        handleBeforeClose(done) {
            this.resetForm("caseDirForm");
            done();
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
            this.dialogTreeMoveCaseVisible = false;
            this.selectedCaseNodeLabel = "";
        },
        // 同步运行单个用例
        handleRunTest(id, name) {
            this.caseRunning = true;
            this.showCancel = true;

            // 创建 cancel token
            this.cancelTokenSource = axios.CancelToken.source();

            // 设置一个定时器，2分钟后执行
            const timeout = setTimeout(() => {
                this.caseRunning = false;
                this.cancelTokenSource.cancel("Request timed out");
            }, 120000); // 120000ms equals to 2 minutes

            this.$api
                .runTestByPkWithCancel(
                    id,
                    {
                        project: this.project,
                        name: name,
                        host: this.host
                    },
                    this.cancelTokenSource.token
                )
                .then(resp => {
                    clearTimeout(timeout); // 清除定时器
                    this.summary = resp;
                    this.dialogTableVisible = true;
                    this.caseRunning = false;
                    this.showCancel = false; // 请求成功完成，隐藏‘取消请求’按钮
                })
                .catch(err => {
                    clearTimeout(timeout); // 清除定时器
                    if (!axios.isCancel(err)) {
                        // 如果错误不是由取消请求引起的，则处理错误
                        this.caseRunning = false;
                        this.$message.error(err);
                    }
                    this.showCancel = false; // 请求失败，隐藏‘取消请求’按钮
                });
        },
        cancelRequest() {
            this.caseRunning = false; // 关闭Loading
            this.showCancel = false; // 隐藏‘取消请求’按钮
            this.cancelTokenSource.cancel("User cancelled the request"); // 取消请求
        },
        /*
         *  异步运行单个用例
         *  @param id 用例id
         *  @param name 用例名称, 测试报告使用这个名称
         */
        handleAsyncRunTest(id, name) {
            this.$api
                .runTestByPk(id, {
                    params: {
                        project: this.project,
                        name: name,
                        host: this.host,
                        async: true
                    }
                })
                .then(resp => {
                    if (resp.success) {
                        this.$message.info({
                            message: resp.msg,
                            duration: 2000,
                            center: true
                        });
                    } else {
                        this.$message.error({
                            message: resp.msg,
                            duration: 2000,
                            center: true
                        });
                    }
                });
        },
        handleCurrentChange() {
            this.$api
                .getTestPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: this.localPageSize,
                        node: this.node,
                        project: this.project,
                        search: this.search,
                        searchType: this.searchType,
                        caseType: this.caseType,
                        creator: this.creator,
                        start_time: (this.dateRange || [])[0],
                        end_time: (this.dateRange || [])[1]
                    }
                })
                .then(resp => {
                    this.testData = resp;
                    this.$emit("update:currentPage", this.localCurrentPage);
                });
        },
        handleSizeChange(newSize) {
            this.localPageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.testData.count / newSize);
            if (this.localCurrentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.localCurrentPage = maxPage;
            }
            this.$api
                .getTestPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: newSize,
                        node: this.node,
                        project: this.project,
                        search: this.search,
                        searchType: this.searchType,
                        caseType: this.caseType,
                        creator: this.creator,
                        start_time: (this.dateRange || [])[0],
                        end_time: (this.dateRange || [])[1]
                    }
                })
                .then(resp => {
                    this.testData = resp;
                    this.$emit("update:pageSize", this.localPageSize);
                });
        },
        handleEditTest(id) {
            this.$api.editTest(id).then(resp => {
                this.$emit("testStep", resp);
                this.$emit("showListBtn", true);
            });
        },
        handleCopyTest(id, name) {
            this.$prompt("请输入用例名称", "提示", {
                closeOnClickModal: false,
                confirmButtonText: "确定",
                inputPattern: /^[\s\S]*\S[\s\S]*$/,
                inputErrorMessage: "用例名称不能为空",
                inputValue: name
            }).then(({ value }) => {
                this.$api
                    .copyTest(id, {
                        name: value,
                        relation: this.node,
                        project: this.project
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message.success("用例复制成功");
                            this.$emit("refreshTree");
                            this.getTestList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
            });
        },
        handleSelectionChange(val) {
            this.selectTest = val;
            // 更新是否已经选择Case, 父组件依赖这个属性来判断是否显示移动用例按钮
            if (this.selectTest.length > 0) {
                this.$emit("update:isSelectCase", true);
            } else {
                this.$emit("update:isSelectCase", false);
            }
        },
        handleDelTest(id) {
            this.$confirm("此操作将永久删除该测试用例, 是否继续", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.delTest(id).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.$emit("refreshTree");
                        this.getTestList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        handleSyncCaseStep(id) {
            this.$confirm("同步测试用例中的用例步骤, 是否继续", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.syncTest(id).then(resp => {
                    if (resp.success) {
                        this.$message.success("用例步骤同步成功");
                        this.getTestList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        resetSearch() {
            this.localPageSize = 10;
            this.localCurrentPage = 1;
            this.searchType = "1";
            this.search = "";
            this.node = "";
            this.creator = this.$store.state.name;
            this.dateRange = [];
            this.caseType = "";
            this.$emit("resetNode");
        },
        caseTypeChangeHandle(command) {
            this.caseType = command;
            this.localCurrentPage = 1;
            this.getTestList();
        },
        searchTypeChangeHandle(value) {
            this.searchType = value;
            this.localCurrentPage = 1;
            this.getTestList();
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        onOpenRunCase() {
            this.getConfig();
        },
        onCloseRunCase() {
            this.currentConfigId = 0;
        },
        getConfig() {
            this.$api.getAllConfig(this.$route.params.id).then(resp => {
                this.configOptions = resp;
                this.configOptions.push({
                    name: "请选择",
                    id: 0
                });
            });
        },
        // 用例批量各类操作
        dropdownMenuChangeHandle(command) {
            const opMap = {
                smoke: 1,
                integrated: 2,
                monitor: 3,
                core: 4
            };
            const tag = opMap[command];
            const case_ids = this.selectTest.map(test => test.id);
            this.$api
                .tagCase({
                    tag: tag,
                    case_ids: case_ids,
                    project_id: this.$route.params.id
                })
                .then(resp => {
                    this.selectTest = [];
                    this.$emit("update:isSelectCase", false);
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.getTestList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
        }
    },
    mounted() {
        this.getTestList();
        this.getUserList();
    }
};
</script>

<style scoped>
.el-select {
    width: 80px;
}

.test-body-table {
    position: fixed;
    bottom: 10px;
    right: 0;
    left: 500px;
    top: 160px;
    padding-bottom: 60px;
    margin-left: -30px;
    z-index: 101;
}

.case__header {
    display: flex;
    align-items: center;
}

.case__header--item {
    display: flex;
    margin-left: 10px;
}

.loading-container {
    position: relative; /* 设置为 relative，以便我们可以在这个容器内使用绝对定位 */
}

.custom-button {
    position: absolute; /* 使用绝对定位 */
    top: calc(50% + 40px); /* 从容器的顶部开始，向下移动50% + 20px */
    left: 50%; /* 从容器的左边开始，向右移动50% */
    transform: translate(-50%, -50%); /* 使用 transform 居中按钮 */
    z-index: 3000; /* 确保按钮在 Loading 动画之上 */
}

.tree-select-option-item {
    background: #fff;
    overflow: scroll;
    height: 200px;
    overflow-x: hidden;
}
</style>
