<template>
    <el-container>
        <el-header style="padding: 0; height: 50px;">
            <div class="recordapi__header">
                <div class="recordapi__header--item">
                    <el-checkbox
                        v-if="apiData.count > 0"
                        v-model="checked"
                        style="padding-top: 14px; padding-left: 2px"
                    ></el-checkbox>
                </div>
                <div class="recordapi__header--item">
                    <el-input
                        placeholder="请输入接口名称"
                        clearable
                        size="small"
                        v-model="search"
                        style="width: 300px"
                    >
                    </el-input>
                </div>

                <div class="recordapi__header--item">
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

                <div class="recordapi__header--item">
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

                <div class="recordapi__header--item">
                    <el-dropdown @command="tagChangeHandle" size="small">
                        <el-button type="primary" size="small">
                            状态
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="0"
                                >未知</el-dropdown-item
                            >
                            <el-dropdown-item command="1"
                                >成功</el-dropdown-item
                            >
                            <el-dropdown-item command="2"
                                >失败</el-dropdown-item
                            >
                            <el-dropdown-item command="">所有</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div class="recordapi__header--item">
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
                >
                    <report :summary="summary"></report>
                </el-dialog>

                <el-dialog
                    title="移动接口"
                    :visible.sync="dialogTreeMoveAPIVisible"
                    :before-close="handleBeforeClose"
                    :close-on-click-modal="false"
                    :style="{ 'text-align': 'center' }"
                    width="30%"
                >
                    <el-form
                        :model="apiDirForm"
                        :rules="apiDirRules"
                        ref="apiDirForm"
                        label-width="100px"
                    >
                        <el-form-item label="接口目录" prop="apiDir">
                            <el-select
                                v-model="selectedApiNodeLabel"
                                value-key="id"
                                placeholder="请选择接口目录"
                                :style="{ width: '100%' }"
                                ref="selectApiNode"
                            >
                                <el-option
                                    :value="selectApiOptionValue"
                                    class="tree-select-option-item"
                                >
                                    <el-tree
                                        :data="dataTree"
                                        :expand-on-click-node="false"
                                        :check-strictly="true"
                                        @node-click="handleApiNodeClick"
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
                        <el-button @click="resetForm('apiDirForm')"
                            >取 消</el-button
                        >
                        <el-button type="primary" @click="moveAPI('apiDirForm')"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>
                <div class="loading-container">
                    <div
                        class="recordapi__body__table"
                        v-loading="tableLoading"
                    >
                        <el-table
                            highlight-current-row
                            v-loading="apiRunning"
                            ref="multipleTable"
                            :data="apiData.results"
                            :show-header="false"
                            :cell-style="{
                                paddingTop: '4px',
                                paddingBottom: '4px'
                            }"
                            height="calc(100%)"
                            style="width: 100%;"
                            @selection-change="handleSelectionChange"
                            @cell-mouse-enter="cellMouseEnter"
                            @cell-mouse-leave="cellMouseLeave"
                        >
                            <el-table-column
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
                                                >选中({{ selectAPI.length }} 条)
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                :disabled="
                                                    selectAPI.length === 0
                                                "
                                                command="success"
                                                >更新为成功
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                :disabled="
                                                    selectAPI.length === 0
                                                "
                                                command="fail"
                                                >更新为失败
                                            </el-dropdown-item>
                                            <el-dropdown-item
                                                :disabled="
                                                    selectAPI.length === 0
                                                "
                                                command="move"
                                                >移动接口
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </el-dropdown>
                                </template>
                            </el-table-column>

                            <el-table-column min-width="325" align="center">
                                <template v-slot="scope">
                                    <div
                                        class="block"
                                        :class="
                                            `block_${scope.row.method.toLowerCase()}`
                                        "
                                    >
                                        <span
                                            class="block-method block_method_color"
                                            :title="
                                                'API分组: ' +
                                                    scope.row.relation_name
                                            "
                                            :class="
                                                `block_method_${scope.row.method.toLowerCase()}`
                                            "
                                            >{{
                                                scope.row.method.toUpperCase()
                                            }}
                                        </span>
                                        <div class="block">
                                            <span
                                                class="block-method block_method_color block_method_options"
                                                v-if="
                                                    scope.row.creator === 'yapi'
                                                "
                                                :title="'从YAPI导入接口'"
                                                >YAPI</span
                                            >
                                        </div>
                                        <span
                                            class="block-method block-api-name-url"
                                            >{{ scope.row.url }}</span
                                        >
                                        <span class="block-api-name-url">{{
                                            scope.row.name
                                        }}</span>
                                        <div>
                                            <span
                                                class="el-icon-s-flag"
                                                v-if="
                                                    scope.row.cases.length > 0
                                                "
                                                :title="
                                                    'API已经被用例引用, 共计：' +
                                                        scope.row.cases.length +
                                                        '次'
                                                "
                                            ></span>
                                        </div>
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column
                                prop="tag"
                                label="标签"
                                width="90"
                                filter-placement="bottom-end"
                            >
                                <template v-slot="scope">
                                    <el-tag
                                        :type="
                                            scope.row.tag === 0
                                                ? 'info'
                                                : scope.row.tag === 2
                                                ? 'danger'
                                                : 'success'
                                        "
                                        effect="light"
                                        >{{ scope.row.tag_name }}</el-tag
                                    >
                                </template>
                            </el-table-column>

                            <el-table-column>
                                <template v-slot="scope">
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
                                                    handleRowClick(scope.row)
                                                "
                                            ></el-button>
                                            <el-button
                                                type="info"
                                                icon="el-icon-document"
                                                title="复制API"
                                                circle
                                                size="mini"
                                                @click="
                                                    handleCopyAPI(
                                                        scope.row.id,
                                                        scope.row.name
                                                    )
                                                "
                                            ></el-button>
                                            <el-button
                                                type="primary"
                                                icon="el-icon-caret-right"
                                                title="运行API"
                                                circle
                                                size="mini"
                                                @click="
                                                    handleRunAPI(
                                                        scope.row.id,
                                                        scope.row.url
                                                    )
                                                "
                                            ></el-button>
                                            <el-popover
                                                style="margin-left: 10px"
                                                trigger="hover"
                                            >
                                                <div style="text-align: center">
                                                    <el-button
                                                        type="danger"
                                                        icon="el-icon-delete"
                                                        :title="
                                                            userId ===
                                                                scope.row
                                                                    .creator ||
                                                            isSuperuser
                                                                ? '删除'
                                                                : '只有API创建者才能删除'
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
                                                            handleDelApi(
                                                                scope.row.id
                                                            )
                                                        "
                                                    ></el-button>
                                                    <el-button
                                                        v-show="
                                                            (userId ===
                                                                scope.row
                                                                    .creator ||
                                                                isSuperuser) &&
                                                                scope.row.cases
                                                                    .length > 0
                                                        "
                                                        :disabled="
                                                            userId !==
                                                                scope.row
                                                                    .creator &&
                                                                !isSuperuser
                                                        "
                                                        type="warning"
                                                        icon="el-icon-refresh"
                                                        :title="
                                                            userId ===
                                                                scope.row
                                                                    .creator ||
                                                            isSuperuser
                                                                ? '同步用例步骤'
                                                                : '同步用例权限不足'
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
                                @size-change="handleSizeChange"
                                @current-change="handleCurrentChange"
                                :page-sizes="[10, 20, 30, 40]"
                                :page-size="localPageSize"
                                :pager-count="5"
                                :current-page.sync="localCurrentPage"
                                :total="apiData.count"
                                v-show="apiData.count > 0"
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
    name: "ApiList",
    components: {
        Report
    },
    props: {
        host: {
            required: false
        },
        config: {
            required: false
        },
        move: Boolean,
        back: Boolean,
        pNode: {
            required: false
        },
        project: {
            required: false
        },
        del: Boolean,
        currentPage: Number,
        pageSize: Number,
        visibleTag: [Number, String],
        rigEnv: [Number, String],
        showYAPI: Boolean,
        isSelectAPI: Boolean
    },
    data() {
        return {
            creator: this.$store.state.name,
            creatorOptions: [],
            dateRange: [],
            isSuperuser: this.$store.state.is_superuser,
            userId: this.$store.state.id,
            checked: false,
            search: "",
            tableLoading: false, // 用于控制表格数据加载的状态
            apiRunning: false, // 用于控制API运行请求的状态
            showCancel: false, // 用于控制取消按钮的显示
            expand: "&#xe65f;",
            dataTree: [],
            selectedApiNodeLabel: "",
            selectApiOptionValue: undefined,
            dialogTreeMoveAPIVisible: false,
            dialogTableVisible: false,
            summary: {},
            selectAPI: [],
            currentRow: "",
            localCurrentPage: this.currentPage || 1,
            localPageSize: this.pageSize || 10,
            node: "",
            apiData: {
                count: 0,
                results: []
            },
            cancelTokenSource: null,
            searchDebounce: null,
            apiDirForm: {
                apiDir: ""
            },
            apiDirRules: {
                apiDir: [
                    {
                        required: true,
                        message: "请选择接口目录",
                        trigger: "change"
                    }
                ]
            }
        };
    },
    watch: {
        search() {
            this.debouncedGetAPIList();
        },
        creator() {
            this.debouncedGetAPIList();
        },
        dateRange() {
            this.debouncedGetAPIList();
        },
        move() {
            this.getTree();
        },
        back() {
            this.debouncedGetAPIList();
        },
        pNode() {
            this.node = this.pNode;
            this.search = "";
            this.debouncedGetAPIList();
        },
        checked() {
            if (this.checked) {
                this.toggleAll();
            } else {
                this.toggleClear();
            }
        },
        del() {
            if (this.selectAPI.length !== 0) {
                this.$confirm("此操作将永久删除接口, 是否继续？", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                })
                    .then(() => {
                        this.$api
                            .delAllAPI({ data: this.selectAPI })
                            .then(res => {
                                this.$message.success(res.msg);
                                this.$emit("refreshTree");
                                this.getAPIList();
                                this.checked = false;
                            });
                    })
                    .catch(e => e);
            } else {
                this.$notify.warning({
                    title: "提示",
                    message: "请先选择API",
                    duration: this.$store.state.duration
                });
            }
        },
        // 监听listCurrentPage的变化，修改原本currentPage的值
        // 因为原来有些函数用到的值是currentPage，所以不能直接修改currentPage的值
        currentPage(newValue) {
            this.localCurrentPage = newValue;
        },
        pageSize(newValue) {
            this.localPageSize = newValue;
        },
        showYAPI() {
            this.debouncedGetAPIList();
        }
    },
    methods: {
        debouncedGetAPIList() {
            clearTimeout(this.searchDebounce);
            this.searchDebounce = setTimeout(() => {
                this.localCurrentPage = 1;
                this.getAPIList();
            }, 300);
        },
        handleApiNodeClick(node) {
            this.apiDirForm.apiDir = node.id;
            this.selectedApiNodeLabel = node.label;
            this.$refs.selectApiNode.toggleMenu();
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
        getAPIList() {
            this.tableLoading = true;
            this.$nextTick(() => {
                this.$api
                    .apiList({
                        params: {
                            page: this.localCurrentPage,
                            size: this.localPageSize,
                            node: this.node,
                            project: this.project,
                            search: this.search,
                            tag: this.visibleTag,
                            rigEnv: this.rigEnv,
                            showYAPI: this.showYAPI,
                            creator: this.creator,
                            start_time: (this.dateRange || [])[0],
                            end_time: (this.dateRange || [])[1]
                        }
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.apiData = resp.data;
                            this.tableLoading = false;
                        } else {
                            this.$message({
                                type: "error",
                                message: resp.msg
                            });
                            this.tableLoading = false;
                        }
                    });
            });
        },
        toggleAll() {
            this.$refs.multipleTable.toggleAllSelection();
        },
        toggleClear() {
            this.$refs.multipleTable.clearSelection();
        },
        tagChangeHandle(command) {
            this.$emit("update:visibleTag", command);
            this.localCurrentPage = 1;
            this.getAPIList();
        },
        dropdownMenuChangeHandle(command) {
            let tag = -1;
            switch (command) {
                case "success":
                    tag = 1;
                    break;
                case "fail":
                    tag = 2;
                    break;
                case "move":
                    this.$emit("update:move", !this.move);
                    break;
            }
            if (command !== "move") {
                let api_ids = [];
                for (let selectAPIElement of this.selectAPI) {
                    api_ids.push(selectAPIElement.id);
                }
                this.$api.tagAPI({ tag: tag, api_ids: api_ids }).then(res => {
                    this.selectAPI = [];
                    this.checked = false;
                    if (res.success) {
                        this.$message({
                            type: "success",
                            message: "标记成功!"
                        });
                        this.getAPIList();
                    } else {
                        this.message({
                            type: "error",
                            message: res.msg
                        });
                    }
                });
            }
        },
        rigEnvChangeHandle(command) {
            this.$emit("update:rigEnv", command);
            this.getAPIList();
        },
        resetSearch() {
            this.search = "";
            this.node = "";
            this.creator = this.$store.state.name;
            this.dateRange = [];
            this.localPageSize = 10;
            this.$emit("update:currentPage", 1);
            this.$emit("update:visibleTag", "");
            this.$emit("update:rigEnv", "");
            this.$emit("update:showYAPI", true);
            this.$emit("resetNode");
        },
        handleCopyAPI(id, name) {
            this.$prompt("请输入接口名称", "提示", {
                closeOnClickModal: false,
                confirmButtonText: "确定",
                inputPattern: /^[\s\S]*\S[\s\S]*$/,
                inputErrorMessage: "接口名称不能为空",
                inputValue: name
            }).then(({ value }) => {
                this.$api
                    .copyAPI(id, {
                        name: value
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message({
                                type: "success",
                                message: "复制成功!"
                            });
                            this.$emit("refreshTree");
                            this.getAPIList();
                        } else {
                            this.$message({
                                type: "error",
                                message: resp.msg
                            });
                        }
                    });
            });
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        moveAPI(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.$api
                        .moveAPI({
                            project: this.project,
                            relation: this.apiDirForm.apiDir,
                            api: this.selectAPI
                        })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success("接口移动成功");
                                this.checked = false;
                                this.$emit("refreshTree");
                                this.getAPIList();
                            } else {
                                this.$message.error(resp.msg);
                            }
                            this.resetForm(formName);
                        });
                }
            });
        },
        handleBeforeClose(done) {
            this.resetForm("apiDirForm");
            done();
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
            this.dialogTreeMoveAPIVisible = false;
            this.selectedApiNodeLabel = "";
        },
        getTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 1 } })
                .then(resp => {
                    this.dataTree = resp.tree;
                    this.dialogTreeMoveAPIVisible = true;
                });
        },
        handleSelectionChange(val) {
            this.selectAPI = val;
            // 更新是否已经选择API, 父组件依赖这个属性来判断是否显示Move API按钮
            if (this.selectAPI.length > 0) {
                this.$emit("update:isSelectAPI", true);
            } else {
                this.$emit("update:isSelectAPI", false);
            }
        },
        handleCurrentChange(val) {
            this.$api
                .getPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: this.localPageSize,
                        node: this.node,
                        project: this.project,
                        search: this.search,
                        tag: this.visibleTag,
                        rigEnv: this.rigEnv,
                        showYAPI: this.showYAPI,
                        creator: this.creator,
                        start_time: (this.dateRange || [])[0],
                        end_time: (this.dateRange || [])[1]
                    }
                })
                .then(resp => {
                    this.apiData = resp.data;
                    this.$emit("click-pager", val);
                });
        },
        handleSizeChange(newSize) {
            this.localPageSize = newSize;
            // 计算新的最大页码
            let maxPage = Math.ceil(this.apiData.count / newSize);
            if (this.localCurrentPage > maxPage) {
                // 如果当前页码超出了范围，请将其设置为最大页面
                this.localCurrentPage = maxPage;
            }
            this.$api
                .getPaginationByPage({
                    params: {
                        page: this.localCurrentPage,
                        size: newSize,
                        node: this.node,
                        project: this.project,
                        search: this.search,
                        tag: this.visibleTag,
                        rigEnv: this.rigEnv,
                        showYAPI: this.showYAPI,
                        creator: this.creator,
                        start_time: (this.dateRange || [])[0],
                        end_time: (this.dateRange || [])[1]
                    }
                })
                .then(resp => {
                    this.apiData = resp.data;
                    this.$emit("update:pageSize", this.localPageSize);
                });
        },
        // 删除api
        handleDelApi(apiId) {
            this.$confirm("此操作将永久删除该API, 是否继续？", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api.delAPI(apiId).then(resp => {
                    if (resp.success) {
                        this.$message.success(resp.msg);
                        this.$emit("refreshTree");
                        this.getAPIList();
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
            });
        },
        // api同步测试用例
        handleSyncCaseStep(id) {
            this.$confirm("是否确定把当前api同步到用例步骤", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api
                    .syncCaseStep(id)
                    .then(resp => {
                        if (resp.success) {
                            this.getAPIList();
                            this.$notify.success({
                                title: "成功",
                                message: "用例步骤同步成功",
                                duration: 2000
                            });
                        } else {
                            this.$message({
                                type: "error",
                                message: resp.msg
                            });
                        }
                    })
                    .catch(err => {
                        this.$message({
                            type: "error",
                            message: err
                        });
                    });
            });
        },
        // 编辑API
        handleRowClick(row) {
            this.$api.getAPISingle(row.id).then(resp => {
                if (resp.success) {
                    this.$emit("api", resp);
                } else {
                    this.$message({
                        type: "error",
                        message: resp.msg
                    });
                }
            });
        },
        // 运行API
        handleRunAPI(id, url) {
            const isUrlValid =
                url.startsWith("http://") || url.startsWith("https://");
            if (!isUrlValid && !this.config.name) {
                this.$message({
                    type: "warning",
                    message: "请先选择配置"
                });
            } else {
                this.apiRunning = true;
                this.showCancel = true;
                // 创建 cancel token
                this.cancelTokenSource = axios.CancelToken.source();
                // 设置一个定时器，2分钟后执行
                const timeout = setTimeout(() => {
                    this.apiRunning = false;
                    this.cancelTokenSource.cancel("Request timed out");
                }, 120000); // 120000ms equals to 2 minutes

                this.$api
                    .runAPIByPk(
                        id,
                        {
                            host: this.host,
                            config: this.config.name
                        },
                        this.cancelTokenSource.token
                    ) // 这里传递 cancel token
                    .then(resp => {
                        clearTimeout(timeout); // 清除定时器
                        this.summary = resp;
                        this.dialogTableVisible = true;
                        this.apiRunning = false;
                        this.showCancel = false; // 请求成功完成，隐藏‘取消请求’按钮
                    })
                    .catch(err => {
                        clearTimeout(timeout); // 清除定时器
                        if (!axios.isCancel(err)) {
                            // 如果错误不是由取消请求引起的，则处理错误
                            this.apiRunning = false;
                            this.$message.error(err);
                        }
                        this.showCancel = false; // 请求失败，隐藏‘取消请求’按钮
                    });
            }
        },
        cancelRequest() {
            this.apiRunning = false; // 关闭Loading
            this.showCancel = false; // 隐藏‘取消请求’按钮
            this.cancelTokenSource.cancel("User cancelled the request"); // 取消请求
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave(row) {
            this.currentRow = "";
        }
    },
    mounted() {
        this.getAPIList();
        this.getUserList();
    }
};
</script>

<style scoped>
.tree-select-option-item {
    background: #fff;
    overflow: scroll;
    height: 200px;
    overflow-x: hidden;
}
.recordapi__header {
    display: flex;
    align-items: center;
}

.recordapi__header--item {
    display: flex;
    margin-left: 10px;
}

.recordapi__body__table {
    position: fixed;
    bottom: 10px;
    right: 0;
    left: 460px;
    top: 160px;
    padding-bottom: 60px;
}

.loading-container {
    position: relative; /* 设置为 relative，以便我们可以在这个容器内使用绝对定位 */
}

.custom-button {
    position: absolute; /* 使用绝对定位 */
    top: calc(50% + 40px); /* 从容器的顶部开始，向下移动50% + 20px */
    left: 50%; /* 从容器的左边开始，向右移动50% */
    transform: translate(-50%, -50%); /* 使用 transform 居中按钮 */
    z-index: 2000; /* 确保按钮在 Loading 动画之上 */
}
</style>
