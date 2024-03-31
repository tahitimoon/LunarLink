<template>
    <el-container>
        <el-header style="background: #fff; padding: 0; height: 50px">
            <div class="nav-api-header">
                <div class="record-api-header">
                    <div style="display: flex; margin-left: 10px">
                        <span class="uniform-text"
                            >录制接口前, 请先配置好app/web代理~（在线体验已关闭此功能）
                            <el-link
                                class="uniform-text"
                                type="primary"
                                :href="$store.state.recordCaseDocsURL"
                                target="_blank"
                                rel="noreferrer"
                                >参考文档</el-link
                            ></span
                        >
                    </div>
                    <div
                        style="display: flex; position: absolute; right: 30px; align-items: center; "
                    >
                        <el-switch
                            style="display: block; margin-right: 10px"
                            :disabled="recordStatus"
                            v-model="isLocalEndpoint"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-text="录制本机"
                            inactive-text="录制其它端"
                        ></el-switch>
                        <el-form
                            class="inline-form"
                            :model="ipUrlRegexForm"
                            :rules="ipUrlRegexRules"
                            ref="ipUrlRegexForm"
                            status-icon
                        >
                            <el-form-item
                                style="margin-bottom: 0;"
                                prop="clientIP"
                                v-if="!isLocalEndpoint"
                            >
                                <el-input
                                    v-model.trim="ipUrlRegexForm.clientIP"
                                    size="small"
                                    style="width: 200px; margin-right: 10px"
                                    placeholder="请输入IP地址, 如127.0.0.1"
                                ></el-input>
                            </el-form-item>
                            <el-form-item
                                style="margin-bottom: 0;"
                                prop="urlRegex"
                            >
                                <el-input
                                    v-model.trim="ipUrlRegexForm.urlRegex"
                                    size="small"
                                    style="width: 360px; margin-right: 10px"
                                    placeholder="请输入要录制的接口地址, 如https://example.com/api"
                                ></el-input>
                            </el-form-item>
                        </el-form>
                        <el-button
                            type="primary"
                            size="small"
                            icon="el-icon-video-camera"
                            @click="startRecord"
                            v-if="!recordStatus"
                            >{{
                                recordCaseData.results.length === 0
                                    ? "开始录制"
                                    : "重新录制"
                            }}</el-button
                        >
                        <el-button
                            type="danger"
                            size="small"
                            icon="el-icon-video-camera"
                            @click="stopRecord()"
                            v-else-if="recordStatus"
                        >
                            停止录制
                        </el-button>
                        <el-button
                            type="primary"
                            size="small"
                            icon="el-icon-refresh"
                            @click="getRecordAPIList"
                            >获取录制接口</el-button
                        >
                        <el-button
                            style="margin-left: 10px"
                            type="success"
                            :disabled="!isSelectRecordAPI"
                            size="small"
                            icon="el-icon-mouse"
                            @click="caseDialogVisible = true"
                            >生成用例</el-button
                        >
                    </div>
                </div>
            </div>
            <el-dialog
                title="生成用例"
                width="30%"
                :visible.sync="caseDialogVisible"
                :before-close="handleBeforeClose"
                :close-on-click-modal="false"
                :style="{ 'text-align': 'center' }"
            >
                <el-form
                    :model="recordCaseForm"
                    :rules="recordCaseRules"
                    ref="recordCaseForm"
                    label-width="100px"
                >
                    <el-form-item label="用例名称" prop="caseName">
                        <el-input
                            v-model.trim="recordCaseForm.caseName"
                            clearable
                            placeholder="请输入用例名称"
                        ></el-input>
                    </el-form-item>

                    <el-form-item label="用例配置" prop="config">
                        <el-select
                            v-model="recordCaseForm.config"
                            value-key="id"
                            placeholder="请选择用例配置"
                            :style="{ width: '100%' }"
                        >
                            <el-option
                                v-for="item in configOptions"
                                :key="item.id"
                                :label="item.name"
                                :value="item.name"
                            ></el-option>
                        </el-select>
                    </el-form-item>

                    <el-form-item label="用例目录" prop="caseDir">
                        <el-select
                            v-model="selectedCaseNodeLabel"
                            value-key="id"
                            placeholder="请选择用例目录"
                            :style="{ width: '100%' }"
                            ref="selectCaseNode"
                        >
                            <el-option
                                :value="selectCaseOptionValue"
                                class="tree-select-option-item"
                            >
                                <el-tree
                                    :data="caseDataTree"
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
                                                    node.childNodes.length > 0
                                                "
                                                class="el-icon-folder-opened"
                                            ></i>
                                            <i v-else class="el-icon-folder"></i
                                            >&nbsp;&nbsp;{{ node.label }}
                                        </span>
                                    </span>
                                </el-tree>
                            </el-option>
                        </el-select>
                    </el-form-item>

                    <div
                        style="display: flex; align-items: center; justify-content: flex-start;"
                    >
                        <el-form-item
                            label="接口目录"
                            prop="apiDir"
                            v-if="isSyncAPI"
                            style="flex-grow: 1; margin-right: 10px; margin-bottom: 0;"
                        >
                            <el-select
                                v-model="selectedApiNodeLabel"
                                value-key="id"
                                placeholder="请选择接口目录"
                                style="width: 100%"
                                ref="selectApiNode"
                            >
                                <el-option
                                    :value="selectApiOptionValue"
                                    class="tree-select-option-item"
                                >
                                    <el-tree
                                        :data="apiDataTree"
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
                                                >&nbsp;&nbsp;{{ node.label }}
                                            </span>
                                        </span>
                                    </el-tree>
                                </el-option>
                            </el-select>
                        </el-form-item>

                        <el-switch
                            v-model="isSyncAPI"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-text="同步API"
                            style="margin-left: 20px; margin-bottom: 0;"
                        ></el-switch>
                    </div>
                </el-form>
                <span
                    slot="footer"
                    class="dialog-footer"
                    style="display: flex; justify-content: flex-end;"
                >
                    <el-button @click="resetForm('recordCaseForm')"
                        >取 消</el-button
                    >
                    <el-button
                        type="primary"
                        @click="handleConfirm('recordCaseForm')"
                        >确 定</el-button
                    >
                </span>
            </el-dialog>
        </el-header>

        <el-container>
            <el-container>
                <el-main class="el-main-table">
                    <div class="record-table">
                        <el-table
                            highlight-current-row
                            stripe
                            :data="currentTableData"
                            v-loading="loading"
                            height="calc(100%)"
                            @cell-mouse-enter="cellMouseEnter"
                            @cell-mouse-leave="cellMouseLeave"
                            @selection-change="handleSelectionChange"
                            :row-key="getRowKeys"
                        >
                            <el-table-column
                                :reserve-selection="true"
                                type="selection"
                                width="55"
                            ></el-table-column>

                            <el-table-column label="编号" width="80">
                                <template slot-scope="scope">
                                    {{
                                        (currentPage - 1) * pageSize +
                                            scope.$index +
                                            1
                                    }}
                                </template>
                            </el-table-column>
                            <el-table-column label="请求地址" width="670">
                                <template slot-scope="scope">
                                    <el-tooltip
                                        :content="scope.row.url"
                                        placement="top"
                                    >
                                        <a
                                            :href="scope.row.url"
                                            class="a-record a-url"
                                            target="_blank"
                                            >{{ scope.row.url }}</a
                                        >
                                    </el-tooltip>
                                </template>
                            </el-table-column>
                            <el-table-column label="请求方式" width="150">
                                <template slot-scope="scope">
                                    <el-tag
                                        :type="
                                            getTagType(scope.row.request_method)
                                        "
                                        size="mini"
                                        >{{ scope.row.request_method }}</el-tag
                                    >
                                </template>
                            </el-table-column>
                            <el-table-column label="请求Headers" width="150">
                                <template slot-scope="scope">
                                    <a
                                        href="#"
                                        class="a-record"
                                        @click.prevent="
                                            showDetails(
                                                scope.row.request_headers,
                                                '请求Headers'
                                            )
                                        "
                                        >详情</a
                                    >
                                </template>
                            </el-table-column>
                            <el-table-column label="请求Body" width="150">
                                <template slot-scope="scope">
                                    <a
                                        v-if="scope.row.body"
                                        href="#"
                                        class="a-record"
                                        @click.prevent="
                                            showDetails(
                                                scope.row.body,
                                                '请求Body'
                                            )
                                        "
                                        >详情</a
                                    >
                                    <span v-else>-</span>
                                </template>
                            </el-table-column>
                            <el-table-column label="响应Headers" width="150">
                                <template slot-scope="scope">
                                    <a
                                        href="#"
                                        class="a-record"
                                        @click.prevent="
                                            showDetails(
                                                scope.row.response_headers,
                                                '响应Headers'
                                            )
                                        "
                                        >详情</a
                                    >
                                </template>
                            </el-table-column>
                            <el-table-column label="Response" width="150">
                                <template slot-scope="scope">
                                    <a
                                        href="#"
                                        class="a-record"
                                        @click.prevent="
                                            showDetails(
                                                scope.row.response_content,
                                                'Response'
                                            )
                                        "
                                        >详情</a
                                    >
                                </template>
                            </el-table-column>
                            <el-table-column label="操作">
                                <template slot-scope="scope">
                                    <el-row v-show="currentRow === scope.row">
                                        <el-button
                                            v-show="recordCaseData.count !== 0"
                                            type="danger"
                                            icon="el-icon-delete"
                                            title="删除"
                                            circle
                                            size="mini"
                                            @click="
                                                handleRemoveRecord(scope.$index)
                                            "
                                        ></el-button>
                                    </el-row>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination-container">
                            <el-pagination
                                background
                                v-show="recordCaseData.results.length !== 0"
                                @size-change="handleSizeChange"
                                @current-change="handleCurrentChange"
                                :current-page.sync="currentPage"
                                :page-sizes="[10, 20, 30, 40]"
                                :page-size="pageSize"
                                :pager-count="5"
                                layout="total, sizes, prev, pager, next"
                                :total="recordCaseData.results.length"
                            ></el-pagination>
                        </div>
                    </div>
                    <el-dialog
                        :visible.sync="recordDialogVisible"
                        :title="dialogTitle"
                        :close-on-click-modal="false"
                        width="50%"
                    >
                        <pre
                            v-html="highlightedCode"
                            class="dialog-code-block"
                        ></pre>
                        <span slot="footer" class="dialog-footer">
                            <el-button
                                type="primary"
                                @click="recordDialogVisible = false"
                                >知道了</el-button
                            >
                        </span>
                    </el-dialog>
                </el-main>
            </el-container>
        </el-container>
    </el-container>
</template>

<script>
import hljs from "highlight.js";
import "highlight.js/styles/vs2015.css";

export default {
    name: "RecordCase",
    components: {},
    data() {
        return {
            isSyncAPI: false,
            isLocalEndpoint: true,
            recordDialogVisible: false,
            caseDialogVisible: false,
            dialogTitle: "",
            highlightedCode: "",
            loading: true,
            isSelectRecordAPI: false,
            currentRow: "",
            pageSize: 10,
            currentPage: 1,
            configOptions: [],
            selectRecordAPI: [],
            selectedCaseNodeLabel: "",
            selectedApiNodeLabel: "",
            selectCaseOptionValue: undefined,
            selectApiOptionValue: undefined,
            caseDataTree: [],
            apiDataTree: [],
            recordStatus: false,
            recordCaseData: {
                results: [],
                regex: "",
                status: false
            },
            ipUrlRegexForm: {
                clientIP: "",
                urlRegex: ""
            },
            ipUrlRegexRules: {
                clientIP: [
                    {
                        required: true,
                        message: "请输入IP地址",
                        trigger: "blur"
                    },
                    {
                        pattern: /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/,
                        message: "请输入有效的IP地址",
                        trigger: "blur"
                    }
                ],
                urlRegex: [
                    {
                        required: true,
                        message: "请输入要录制的接口地址",
                        trigger: "blur"
                    }
                ]
            },
            recordCaseForm: {
                config: "",
                caseDir: "",
                apiDir: "",
                caseName: ""
            },
            recordCaseRules: {
                config: [
                    {
                        required: true,
                        message: "请选择配置",
                        trigger: "change"
                    }
                ],
                caseDir: [
                    {
                        required: true,
                        message: "请选择用例目录",
                        trigger: "change"
                    }
                ],
                caseName: [
                    {
                        required: true,
                        message: "请输入用例名称",
                        trigger: "blur"
                    },
                    {
                        min: 0,
                        max: 50,
                        message: "最多不超过50个字符",
                        trigger: "blur"
                    }
                ]
            }
        };
    },
    watch: {
        isSyncAPI(newValue) {
            if (newValue) {
                this.recordCaseRules.apiDir = [
                    {
                        required: true,
                        message: "请选择接口目录",
                        trigger: "change"
                    }
                ];
            } else {
                delete this.recordCaseRules.apiDir;
            }
        }
    },
    computed: {
        currentTableData() {
            const startIndex = (this.currentPage - 1) * this.pageSize;
            const endIndex = startIndex + this.pageSize;
            return this.recordCaseData.results.slice(startIndex, endIndex);
        },
        getTagType() {
            return requestMethod => {
                switch (requestMethod) {
                    case "POST":
                        return "success";
                    case "GET":
                        return "";
                    case "PUT":
                        return "warning";
                    case "DELETE":
                        return "danger";
                    default:
                        return "info";
                }
            };
        }
    },
    methods: {
        computedIndex(index) {
            return (this.currentPage - 1) * this.pageSize + index + 1;
        },
        getRowKeys(row) {
            return row.id;
        },
        showDetails(data, title) {
            this.dialogTitle = title;

            let jsonData;
            if (typeof data === "string") {
                try {
                    jsonData = JSON.parse(data);
                } catch (e) {
                    jsonData = data;
                }
            } else {
                jsonData = data;
            }

            this.highlightedCode = hljs.highlight(
                "json",
                JSON.stringify(jsonData, null, 4)
            ).value;
            this.recordDialogVisible = true;
        },

        getCurrentIP() {
            return this.isLocalEndpoint ? "" : this.ipUrlRegexForm.clientIP;
        },
        startRecord() {
            this.$refs.ipUrlRegexForm.validate(valid => {
                if (valid) {
                    const ip = this.getCurrentIP();
                    const regex = this.ipUrlRegexForm.urlRegex;
                    const isLocalEndpoint = this.isLocalEndpoint;
                    this.tryToStartRecord(ip, regex, isLocalEndpoint);
                } else {
                    return false;
                }
            });
        },
        tryToStartRecord(ip, regex, isLocalEndpoint) {
            this.$api
                .recordStart({
                    params: {
                        ip: ip,
                        regex: regex,
                        local: isLocalEndpoint
                    }
                })
                .then(resp => {
                    if (resp.success) {
                        this.recordStatus = true;
                        this.$message.success(resp.msg);
                    } else if (resp.code === "0005") {
                        // 当前IP已经在录制中，提示用户
                        this.$confirm("此IP正在录制中, 是否重新录制?", "提示", {
                            confirmButtonText: "确定",
                            cancelButtonText: "取消",
                            type: "warning"
                        })
                            .then(() => {
                                // 用户确认重新录制
                                this.stopRecord(ip, false).then(() => {
                                    // 停止成功后，重新开始录制
                                    this.tryToStartRecord(ip, regex);
                                });
                            })
                            .catch(() => {
                                // 用户取消操作
                            });
                    } else {
                        // 其他错误，恢复开始录制按钮
                        this.recordStatus = false;
                        this.$message.error(resp.msg);
                    }
                });
        },
        stopRecord(ip, showSuccessMessage = true) {
            if (!ip) {
                ip = this.getCurrentIP();
            }
            return new Promise((resolve, reject) => {
                this.$api
                    .recordStop({
                        params: { ip: ip }
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.recordStatus = false;
                            if (showSuccessMessage) {
                                this.$message.success(resp.msg);
                            }
                            resolve();
                        } else {
                            this.$message.error(resp.msg);
                            reject();
                        }
                    });
            });
        },
        handleSelectionChange(val) {
            // val 是当前选中的行数组，但顺序是用户选择的顺序
            // this.currentTableData 是当前页面表格的数据，按照表格的顺序
            // 使用 filter 方法，根据 currentTableData 的顺序重新构建选中项数组
            this.selectRecordAPI = this.currentTableData.filter(row =>
                val.includes(row)
            );
            // 更新是否已经选择录制API, 依赖这个属性来判断是否禁用生成用例按钮
            this.isSelectRecordAPI = this.selectRecordAPI.length > 0;
        },
        cellMouseEnter(row) {
            this.currentRow = row;
        },
        cellMouseLeave() {
            this.currentRow = "";
        },
        handleRemoveRecord(index) {
            const ip = this.isLocalEndpoint ? "" : this.ipUrlRegexForm.clientIP;
            const globalIndex = this.computedIndex(index) - 1;
            this.$confirm("删除录制接口，是否继续?", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            }).then(() => {
                this.$api
                    .recordRemove({
                        params: { index: globalIndex, ip: ip }
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message.success(resp.msg);
                            this.getRecordAPIList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
            });
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            this.currentPage = 1;
        },
        handleCurrentChange(newPage) {
            this.currentPage = newPage;
        },
        getRecordAPIList() {
            const ip = this.isLocalEndpoint ? "" : this.ipUrlRegexForm.clientIP;
            this.$api
                .getRecordStatus({
                    params: {
                        ip: ip
                    }
                })
                .then(resp => {
                    this.recordCaseData = {
                        // 使用展开运算符复制resp对象中的所有属性到recordCaseData中
                        ...resp,
                        // 使用map函数处理resp.results数组，为每个元素添加一个唯一标识符id
                        results: resp.results.map((item, index) => ({
                            // 使用展开运算符复制当前元素（item）的所有属性
                            ...item,
                            // 使用数组的索引index作为新属性id的值，提供一个唯一标识符
                            id: index
                        }))
                    };
                    // 正在录制时，更新url和录制状态
                    this.ipUrlRegexForm.urlRegex = this.recordCaseData.regex;
                    if (!this.recordCaseData.local) {
                        this.ipUrlRegexForm.clientIP = this.recordCaseData.ip;
                    }
                    this.isLocalEndpoint = this.recordCaseData.local;
                    this.recordStatus = this.recordCaseData.status;
                    this.loading = false;
                });
        },
        handleConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    const caseConfig = {
                        body: {
                            name: this.recordCaseForm.config,
                            method: "config"
                        }
                    };
                    this.$api
                        .generateTestCase({
                            name: this.recordCaseForm.caseName,
                            length: this.selectRecordAPI.length,
                            project: this.$route.params.id,
                            case_dir: this.recordCaseForm.caseDir,
                            api_dir: this.recordCaseForm.apiDir,
                            config: caseConfig,
                            requests: this.selectRecordAPI
                        })
                        .then(resp => {
                            if (resp.success) {
                                this.$message.success(resp.msg);
                            } else {
                                this.$message.error(resp.msg);
                            }
                            this.resetForm(formName);
                        });
                }
            });
        },
        handleBeforeClose(done) {
            this.resetForm("recordCaseForm");
            done();
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
            this.caseDialogVisible = false;
            this.isSyncAPI = false;
            this.selectedApiNodeLabel = "";
            this.selectedCaseNodeLabel = "";
        },
        getConfig() {
            this.$api.getAllConfig(this.$route.params.id).then(resp => {
                this.configOptions = resp;
                const _config = this.configOptions.filter(
                    item => item.is_default === true
                );
                if (_config.length) {
                    this.recordCaseForm.config = _config[0].name;
                }
            });
        },
        getCaseTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 2 } })
                .then(resp => {
                    this.caseDataTree = resp.tree;
                });
        },
        getApiTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 1 } })
                .then(resp => {
                    this.apiDataTree = resp.tree;
                });
        },
        handleCaseNodeClick(node) {
            this.recordCaseForm.caseDir = node.id;
            this.selectedCaseNodeLabel = node.label;
            this.$refs.selectCaseNode.toggleMenu();
        },
        handleApiNodeClick(node) {
            this.recordCaseForm.apiDir = node.id;
            this.selectedApiNodeLabel = node.label;
            this.$refs.selectApiNode.toggleMenu();
        }
    },
    mounted() {
        this.getConfig();
        this.getCaseTree();
        this.getApiTree();
        this.getRecordAPIList();
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

.dialog-code-block {
    background-color: black;
    padding: 16px;
    max-width: 100%;
    overflow-x: auto;
    white-space: pre-wrap; /* 保持换行符 */
    word-wrap: break-word; /* 在单词边界处断行 */
}
.a-record {
    color: #409eff;
    text-decoration: none;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.record-table {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 220px;
    top: 100px;
    margin-left: -10px;
    padding-bottom: 60px;
}

.el-main-table {
    padding: 0;
    margin-left: 10px;
    margin-top: 10px;
}

.record-api-header {
    display: flex;
    height: 50px;
    justify-content: flex-start;
    align-items: center;
}

.el-tree-span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 0 1 auto;
}

.uniform-text {
    font-size: 14px;
    line-height: 1.5;
}

.inline-form {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
}
</style>
