<template>
    <el-container>
        <el-header style="background: #ffffff; padding: 0;">
            <div>
                <div class="nav-api-header">
                    <div
                        style="display: flex; padding-top: 10px; padding-left: 10px; align-items: center;"
                    >
                        <el-button
                            :style="
                                userName !== projectInfo.responsible &&
                                !isSuperuser
                                    ? 'margin-right: 10px'
                                    : ''
                            "
                            :disabled="currentNode === ''"
                            v-show="!addAPIFlag"
                            type="primary"
                            size="small"
                            icon="el-icon-circle-plus-outline"
                            @click="initResponse = true"
                            >添加接口</el-button
                        >

                        <el-button
                            style="margin-right: 10px"
                            v-show="
                                (userName === projectInfo.responsible &&
                                    !addAPIFlag) ||
                                    (isSuperuser && !addAPIFlag)
                            "
                            type="primary"
                            size="small"
                            icon="el-icon-upload"
                            @click="importYAPIdialogVisible = true"
                            >导入接口</el-button
                        >

                        <span>配置</span>
                        <el-select
                            style="margin-left: 10px"
                            placeholder="请选择配置"
                            size="small"
                            v-model="currentConfig"
                            value-key="id"
                        >
                            <el-option
                                v-for="item in configOptions"
                                :key="item.id"
                                :label="item.name"
                                :value="item"
                            ></el-option>
                        </el-select>

                        <el-button
                            style="margin-left: 10px"
                            v-if="!addAPIFlag"
                            :disabled="!(!addAPIFlag && isSelectAPI)"
                            type="success"
                            size="mini"
                            icon="el-icon-right"
                            @click="move = !move"
                            :title="'移动接口到指定目录'"
                            >移动接口</el-button
                        >

                        <el-button
                            style="margin-left: 10px"
                            v-if="isSuperuser && !addAPIFlag"
                            type="danger"
                            icon="el-icon-delete"
                            size="mini"
                            :title="
                                isSuperuser === true
                                    ? '批量删除所选接口'
                                    : '批量删除接口权限不足'
                            "
                            :disabled="!(isSuperuser && isSelectAPI)"
                            @click="del = !del"
                            >批量删除</el-button
                        >

                        <el-switch
                            style="margin-left: 10px"
                            v-model="showYAPI"
                            v-if="!addAPIFlag"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-text="显示YAPI"
                        ></el-switch>

                        <el-button
                            :disabled="!addAPIFlag"
                            type="text"
                            style="position: absolute; right: 30px"
                            @click="handleBackList"
                            >返回列表</el-button
                        >
                    </div>
                </div>
                <el-dialog
                    title="新建目录"
                    width="30%"
                    :visible.sync="dialogVisible"
                    :close-on-click-modal="false"
                    :style="{ 'text-align': 'center' }"
                >
                    <el-form
                        :model="nodeForm"
                        :rules="rules"
                        ref="nodeForm"
                        label-width="100px"
                        class="project"
                    >
                        <el-form-item label="目录名称" prop="name">
                            <el-input
                                v-model="nodeForm.name"
                                placeholder="请输入目录名称"
                            ></el-input>
                        </el-form-item>
                    </el-form>

                    <el-radio-group v-model="radio" size="small">
                        <el-radio-button label="根目录"></el-radio-button>
                        <el-radio-button label="子目录"></el-radio-button>
                    </el-radio-group>

                    <span
                        slot="footer"
                        class="dialog-footer"
                        style="display: flex; justify-content: flex-end"
                    >
                        <el-button @click="dialogVisible = false"
                            >取 消</el-button
                        >
                        <el-button
                            type="primary"
                            @click="handleConfirm('nodeForm')"
                            >确 定</el-button
                        >
                    </span>
                </el-dialog>
                <el-dialog
                    width="30%"
                    title="导入YAPI接口"
                    :style="{ 'text-align': 'center' }"
                    :visible.sync="importYAPIdialogVisible"
                >
                    <el-form
                        ref="elForm"
                        :model="YAPIformData"
                        :rules="rules"
                        size="medium"
                        label-width="100px"
                    >
                        <el-form-item label="YAPI的地址" prop="yapi_base_url">
                            <el-input
                                v-model="YAPIformData.yapi_base_url"
                                readonly
                                placeholder="请输入YAPI的地址"
                                clearable
                                :style="{ width: '100%' }"
                            ></el-input>
                        </el-form-item>
                        <el-form-item label="token" prop="yapi_openapi_token">
                            <el-input
                                v-model="YAPIformData.yapi_openapi_token"
                                readonly
                                placeholder="请输入openapi token"
                                clearable
                                :style="{ width: '100%' }"
                            ></el-input>
                        </el-form-item>
                    </el-form>
                    <div
                        style="display: flex; justify-content: right;"
                        slot="footer"
                        class="dialog-footer"
                    >
                        <el-button @click="importYAPIdialogVisible = false"
                            >取消</el-button
                        >
                        <el-button
                            type="primary"
                            @click="handleConfirmYAPI"
                            :title="
                                YAPIformData.yapi_openapi_token ===
                                    YAPIfromDataDefaultValue ||
                                YAPIformData.yapi_base_url ===
                                    YAPIfromDataDefaultValue
                                    ? '请到项目详情中配置yapi信息'
                                    : '导入YAPI目录和接口'
                            "
                            :disabled="
                                YAPIformData.yapi_openapi_token ===
                                    YAPIfromDataDefaultValue ||
                                    YAPIformData.yapi_base_url ===
                                        YAPIfromDataDefaultValue
                            "
                            >导入</el-button
                        >
                    </div>
                </el-dialog>
            </div>
        </el-header>

        <el-container>
            <el-aside
                v-show="!addAPIFlag"
                style="width: 260px; margin-top: 10px;"
            >
                <div class="nav-api-side">
                    <div class="api-tree">
                        <el-input
                            placeholder="请输入关键字进行过滤"
                            v-model="filterText"
                            size="small"
                            clearable
                            prefix-icon="el-icon-search"
                        ></el-input>
                        <el-tree
                            ref="tree2"
                            node-key="id"
                            @node-drag-start="handleDragStart"
                            @node-click="handleNodeClick"
                            @node-drag-end="handleDragEnd"
                            @node-expand="handleNodeExpand"
                            @node-collapse="handleNodeCollapse"
                            draggable
                            highlight-current
                            :filter-node-method="filterNode"
                            :data="dataTree"
                            :default-expanded-keys="expandedNodeIds"
                            :default-expand-all="false"
                            :expand-on-click-node="false"
                        >
                            <span
                                class="custom-tree-node"
                                slot-scope="{ node, data }"
                                @mouseenter="mouseenter(node)"
                                @mouseleave="mouseleave"
                            >
                                <span class="custom-tree-node-span">
                                    <i
                                        v-if="node.childNodes.length > 0"
                                        class="el-icon-folder-opened"
                                    ></i>
                                    <i v-else class="el-icon-folder"></i>
                                    &nbsp;&nbsp;{{ node.label }}
                                </span>

                                <span style="flex-shrink: 0; margin-left: 5px;">
                                    <el-badge
                                        :value="data.data_count"
                                        :max="99"
                                        type="primary"
                                    ></el-badge>
                                </span>

                                <span
                                    class="icon-group"
                                    v-show="node.id === mouseNodeId"
                                >
                                    <i
                                        class="el-icon-folder-add"
                                        @click="dialogVisible = true"
                                    ></i>
                                    <i
                                        class="el-icon-edit"
                                        @click="renameNode(node)"
                                    ></i>
                                    <i
                                        class="el-icon-delete"
                                        @click="deleteNode(node)"
                                    ></i>
                                </span>
                            </span>
                        </el-tree>
                    </div>
                </div>
            </el-aside>

            <el-main style="padding: 0;">
                <api-body
                    v-show="addAPIFlag"
                    :isSaveAs="isSaveAs"
                    :nodeId="currentNode.id"
                    :project="$route.params.id"
                    :response="response"
                    :config="currentConfig"
                    :host="currentHost"
                    @addSuccess="handleAddSuccess"
                    @refreshTree="getTree"
                    @otherContentChanged="handleOtherContentChange"
                    @headerContentChanged="handleHeaderContentChange"
                    @requestContentChanged="handleRequestContentChange"
                    @extractContentChanged="handleExtractContentChange"
                    @validateContentChanged="handleValidateContentChange"
                    @variablesContentChanged="handleVariablesContentChange"
                    @hooksContentChanged="handleHooksContentChange"
                ></api-body>
                <api-list
                    v-show="!addAPIFlag"
                    :p-node="currentNode !== '' ? currentNode.id : ''"
                    :project="$route.params.id"
                    :config="currentConfig"
                    :host="currentHost"
                    :del="del"
                    :back="back"
                    :move.sync="move"
                    :current-page.sync="currentPage"
                    :page-size.sync="pageSize"
                    :visibleTag.sync="visibleTag"
                    :rigEnv.sync="rigEnv"
                    :showYAPI.sync="showYAPI"
                    :isSelectAPI.sync="isSelectAPI"
                    @api="handleAPI"
                    @click-pager="handleChangePage"
                    @resetNode="resetNodeStatus"
                    @refreshTree="getTree"
                ></api-list>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import ApiBody from "./components/ApiBody";
import ApiList from "./components/ApiList";

export default {
    name: "RecordApi",
    components: {
        ApiBody,
        ApiList
    },
    watch: {
        filterText(val) {
            this.$refs.tree2.filter(val);
        }
    },
    computed: {
        initResponse: {
            get() {
                return this.addAPIFlag;
            },
            set(val) {
                this.addAPIFlag = val;
                this.isSaveAs = false;
                this.response = {
                    id: "",
                    body: {
                        name: "",
                        times: 1,
                        url: "",
                        method: "POST",
                        header: [
                            {
                                key: "",
                                value: "",
                                desc: ""
                            }
                        ],
                        request: {
                            data: [
                                {
                                    key: "",
                                    value: "",
                                    desc: "",
                                    type: 1
                                }
                            ],
                            params: [
                                {
                                    key: "",
                                    value: "",
                                    desc: "",
                                    type: 1
                                }
                            ],
                            json_data: ""
                        },
                        validate: [
                            {
                                expect: "200",
                                actual: "status_code",
                                comparator: "equals",
                                type: 2,
                                desc: "默认断言"
                            }
                        ],
                        variables: [
                            {
                                key: "",
                                value: "",
                                desc: "",
                                type: 1
                            }
                        ],
                        extract: [
                            {
                                key: "",
                                value: "",
                                desc: ""
                            }
                        ],
                        hooks: [
                            {
                                setup: "",
                                teardown: ""
                            }
                        ]
                    }
                };
            }
        }
    },
    data() {
        const YAPIformDataDefaultValue = "请到项目详情编辑";
        return {
            isOtherContentChanged: false,
            isHeaderContentChanged: false,
            isRequestContentChanged: false,
            isExtractContentChanged: false,
            isValidateContentChanged: false,
            isVariablesContentChanged: false,
            isHooksContentChanged: false,
            expandedNodeIds: [],
            originalTreeData: [],
            mouseNodeId: -1,
            isSuperuser: this.$store.state.is_superuser,
            userName: this.$store.state.name,
            projectInfo: {
                responsible: ""
            },
            configOptions: [],
            hostOptions: [],
            currentConfig: "",
            currentHost: "请选择",
            back: false,
            del: false,
            move: false,
            response: "",
            nodeForm: {
                name: ""
            },
            rules: {
                yapi_base_url: [
                    {
                        required: true,
                        message: "yapi的openapi url",
                        trigger: "blur"
                    }
                ],
                yapi_openapi_token: [
                    {
                        required: true,
                        message: "yapi的openapi token",
                        trigger: "blur"
                    }
                ],
                name: [
                    {
                        required: true,
                        message: "请输入目录名称",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 50,
                        message: "最多不超过50个字符",
                        trigger: "blur"
                    }
                ]
            },
            radio: "根目录",
            addAPIFlag: false,
            treeId: "",
            maxId: "",
            dialogVisible: false,
            importYAPIdialogVisible: false,
            currentNode: "",
            data: "",
            filterText: "",
            expand: "&#xe65f",
            dataTree: [],
            currentPage: 1,
            pageSize: 10,
            visibleTag: "",
            rigEnv: "",
            showYAPI: true,
            isSelectAPI: false,
            isSaveAs: false,
            YAPIfromDataDefaultValue: YAPIformDataDefaultValue,
            YAPIformData: {
                yapi_base_url: YAPIformDataDefaultValue,
                yapi_openapi_token: YAPIformDataDefaultValue
            }
        };
    },
    methods: {
        handleDragStart() {
            // 保存当前树的状态
            this.originalTreeData = JSON.parse(JSON.stringify(this.dataTree));
        },
        handleNodeExpand(node) {
            // 当一个目录被展开时，将它的 ID 添加到 expandedNodeIds 中
            if (!this.expandedNodeIds.includes(node.id)) {
                this.expandedNodeIds.push(node.id);
            }
        },
        handleNodeCollapse(node) {
            // 当一个目录被收起时，将它的 ID 从 expandedNodeIds 中移除并且移除所有子节点
            // 移除当前节点 ID
            const index = this.expandedNodeIds.indexOf(node.id);
            if (index !== -1) {
                this.expandedNodeIds.splice(index, 1);
            }

            // 递归移除所有子节点 ID
            if (node.children && node.children.length > 0) {
                node.children.forEach(childNode => {
                    this.handleNodeCollapse(childNode);
                });
            }
        },
        // 将目录的状态恢复到未选中状态
        resetNodeStatus() {
            this.$refs.tree2.setCurrentKey(null);
            this.currentNode = "";
        },
        handleDragEnd() {
            this.$confirm("确定要移动这个目录吗?", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            })
                .then(() => {
                    // 用户确认拖拽操作，更新树形结构
                    this.updateTree();
                })
                .catch(() => {
                    // 用户取消操作，恢复原始树形结构
                    this.dataTree = JSON.parse(
                        JSON.stringify(this.originalTreeData)
                    );
                });
        },
        handleAddSuccess() {
            this.currentPage = 1;
            this.pageSize = 10;
            this.rigEnv = "";
            this.visibleTag = "";
            this.back = !this.back;
            this.addAPIFlag = false;
            this.isSaveAs = false;
        },
        handleAPI(response) {
            this.addAPIFlag = true;
            this.response = response;
            this.isSaveAs = true;
        },
        handleChangePage(val) {
            this.currentPage = val;
        },
        getTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 1 } })
                .then(resp => {
                    this.dataTree = resp["tree"];
                    this.treeId = resp["id"];
                    this.maxId = resp["max"];
                });
        },
        getConfig() {
            this.$api.getAllConfig(this.$route.params.id).then(resp => {
                this.configOptions = resp;
                const _config = this.configOptions.filter(
                    item => item.is_default === true
                );
                if (_config.length) {
                    this.currentConfig = _config[0];
                }
            });
        },
        // 准备树形数据以供更新
        prepareTreeDataForUpdate(treeData) {
            return treeData.map(node => {
                // 创建一个不包含 data_count 字段的新对象
                const { data_count, ...nodeWithoutDataCount } = node;

                // 如果有 children 字段，递归处理子目录
                if (node.children && node.children.length > 0) {
                    return {
                        ...nodeWithoutDataCount,
                        children: this.prepareTreeDataForUpdate(node.children)
                    };
                }

                // 返回处理后的目录
                return nodeWithoutDataCount;
            });
        },
        updateTree() {
            const preparedData = this.prepareTreeDataForUpdate(this.dataTree);
            this.$api
                .updateTree(this.treeId, {
                    body: preparedData,
                    type: 1
                })
                .then(resp => {
                    if (resp["success"]) {
                        this.dataTree = resp["data"]["tree"];
                        this.maxId = resp["data"]["max"];
                        this.$message.success("目录更新成功");
                    } else {
                        this.$message.error(resp.msg);
                    }
                });
        },
        deleteNode(node) {
            this.$confirm(
                `删除 ${node.label} 目录下所有接口, 是否继续?`,
                "提示",
                {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                }
            ).then(() => {
                if (this.currentNode === "") {
                    this.$message.info("请选择一个目录");
                } else {
                    let dataCopy = JSON.parse(JSON.stringify(this.dataTree)); // 创建树形数据的拷贝
                    this.removeNodeFromData(this.currentNode.id, dataCopy); // 从拷贝的数据中移除目录
                    this.$api
                        .updateTree(this.treeId, {
                            body: dataCopy, // 发送已经移除目录的数据
                            type: 1
                        })
                        .then(resp => {
                            if (resp["success"]) {
                                this.dataTree = resp["data"]["tree"]; // 更新前端的树形数据
                                this.maxId = resp["data"]["max"];
                                this.$message.success("目录更新成功");
                            } else {
                                this.$message.error(resp.msg);
                            }
                        });
                }
            });
        },
        removeNodeFromData(nodeId, data) {
            for (let i = 0; i < data.length; i++) {
                if (data[i].id === nodeId) {
                    data.splice(i, 1);
                    break;
                } else if (data[i].children) {
                    this.removeNodeFromData(nodeId, data[i].children);
                }
            }
        },
        renameNode(nodeObj) {
            this.$prompt("请输入目录名", "编辑", {
                closeOnClickModal: false,
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                inputPattern: /\S/,
                inputErrorMessage: "目录名不能为空",
                inputValue: nodeObj.label
            }).then(({ value }) => {
                const parent = this.data.parent;
                const children = parent.data.children || parent.data;
                const index = children.findIndex(
                    d => d.id === this.currentNode.id
                );
                children[index].label = value;
                this.updateTree();
            });
        },
        handleConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.append(this.currentNode);
                    this.updateTree();
                    this.dialogVisible = false;
                    this.nodeForm.name = "";
                }
            });
        },
        handleNodeClick(node, data) {
            // 点击子目录把页码重置设置为1
            this.currentPage = 1;
            this.visibleTag = "";
            this.addAPIFlag = false;
            this.isSaveAs = false;
            this.currentNode = node;
            this.data = data;
            this.rigEnv = "";
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        remove(data, node) {
            const parent = node.parent;
            const children = parent.data.children || parent.data;
            const index = children.findIndex(d => d.id === data.id);
            children.splice(index, 1);
        },
        append(data) {
            const newChild = {
                id: ++this.maxId,
                label: this.nodeForm.name,
                children: []
            };
            if (
                data === "" ||
                this.dataTree.length === 0 ||
                this.radio === "根目录"
            ) {
                this.dataTree.push(newChild);
                return;
            }
            if (!data.children) {
                this.$set(data, "children", []);
            }
            data.children.push(newChild);
            if (this.radio === "子目录") {
                this.expandedNodeIds.push(data.id); // 添加当前父目录的 id
            }
        },
        handleOtherContentChange(hasChanged) {
            this.isOtherContentChanged = hasChanged;
        },
        handleHeaderContentChange(hasChanged) {
            this.isHeaderContentChanged = hasChanged;
        },
        handleRequestContentChange(hasChanged) {
            this.isRequestContentChanged = hasChanged;
        },
        handleExtractContentChange(hasChanged) {
            this.isExtractContentChanged = hasChanged;
        },
        handleValidateContentChange(hasChanged) {
            this.isValidateContentChanged = hasChanged;
        },
        handleVariablesContentChange(hasChanged) {
            this.isVariablesContentChanged = hasChanged;
        },
        handleHooksContentChange(hasChanged) {
            this.isHooksContentChanged = hasChanged;
        },
        closeEditor() {
            this.addAPIFlag = false;
            this.isSaveAs = false;
        },
        handleBackList() {
            if (
                this.isOtherContentChanged ||
                this.isHeaderContentChanged ||
                this.isRequestContentChanged ||
                this.isExtractContentChanged ||
                this.isValidateContentChanged ||
                this.isVariablesContentChanged ||
                this.isHooksContentChanged
            ) {
                this.$confirm("内容未保存，确定关闭？", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                })
                    .then(() => {
                        // 用户确认关闭
                        this.closeEditor();
                    })
                    .catch(() => {
                        // 用户取消关闭
                    });
            } else {
                // 没有变化，直接关闭
                this.closeEditor();
            }
        },
        getYapiInfo() {
            const pk = this.$route.params.id;
            this.$api.getProjectYapiInfo(pk).then(resp => {
                this.projectInfo = resp;
                if (resp.yapi_base_url !== "") {
                    this.YAPIformData.yapi_base_url = resp.yapi_base_url;
                }
                if (resp.yapi_openapi_token !== "") {
                    this.YAPIformData.yapi_openapi_token =
                        resp.yapi_openapi_token;
                }
            });
        },
        mouseenter(node) {
            this.mouseNodeId = node.id;
        },
        mouseleave() {
            this.mouseNodeId = -1;
        },
        handleConfirmYAPI() {
            this.$refs["elForm"].validate(valid => {
                if (!valid) return;
                const projectId = this.$route.params.id;
                this.$message.info("如果是首次导入，可能时间稍长，请稍后查看~");
                this.importYAPIdialogVisible = false;
                this.$api.addYAPI(projectId).then(resp => {
                    if (resp.success) {
                        let created = "新增: " + resp.createdCount + " 条API";
                        let updated = "更新: " + resp.updatedCount + " 条API";
                        if (resp.createdCount > 0 || resp.updatedCount > 0) {
                            this.$notify.success({
                                title: "导入API提示",
                                message: created + " ; " + updated,
                                duration: this.$store.state.duration
                            });
                        }
                        const NOT_CREATED_AND_UPDATED_CODE = "0002";
                        if (resp.code === NOT_CREATED_AND_UPDATED_CODE) {
                            this.$notify.info({
                                title: "导入API提示",
                                message: resp.msg,
                                duration: this.$store.state.duration
                            });
                        }
                        const CREATED_OR_UPDATED_CODE = "0001";
                        if (resp.code === CREATED_OR_UPDATED_CODE) {
                            this.getTree();
                            // 重置tree目录, 触发子组件更新api
                            // TODO: 改成直接调用子组件的getAPIList方法
                            this.currentNode = "";
                            this.showYAPI = true;
                        }
                    } else {
                        this.$message.error({
                            message: resp.msg,
                            duration: this.$store.state.duration
                        });
                    }
                });
            });
        }
    },
    mounted() {
        this.getTree();
        this.getConfig();
        this.getYapiInfo();
    }
};
</script>

<style scoped>
.icon-group {
    margin-right: 6px;
}

.icon-group i {
    margin-left: 4px;
    padding: 2px;
}
</style>
