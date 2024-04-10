<template>
    <el-container>
        <el-header style="background: #fff; padding: 0; height: 50px;">
            <div class="nav-api-header">
                <div style="display: flex; padding: 10px; align-items: center;">
                    <el-button
                        type="primary"
                        size="small"
                        icon="el-icon-circle-plus-outline"
                        @click="buttonActivate = false"
                        :disabled="buttonActivate"
                        >添加用例</el-button
                    >
                    <span style="margin-left: 10px">配置</span>
                    <el-select
                        placeholder="请选择配置"
                        size="small"
                        v-model="currentConfig"
                        :disabled="addTestActivate"
                        style="margin-left: 10px;"
                        value-key="id"
                    >
                        <el-option
                            v-for="item in configOptions"
                            :key="item.id"
                            :label="item.name"
                            :value="item.name"
                        ></el-option>
                    </el-select>
                    <el-button
                        style="margin-left: 10px"
                        v-if="addTestActivate"
                        type="primary"
                        size="mini"
                        title="批量运行用例"
                        icon="el-icon-caret-right"
                        @click="run = !run"
                        >批量运行</el-button
                    >
                    <el-button
                        v-if="addTestActivate"
                        :disabled="!isSelectCase"
                        type="success"
                        size="mini"
                        icon="el-icon-right"
                        title="移动用例到指定目录"
                        @click="move = !move"
                        >移动用例</el-button
                    >
                    <el-button
                        v-if="addTestActivate"
                        :disabled="!isSelectCase"
                        type="danger"
                        icon="el-icon-delete"
                        size="mini"
                        title="批量删除用例"
                        @click="del = !del"
                        >批量删除</el-button
                    >
                    <el-button
                        v-show="isShowListBtn"
                        type="text"
                        style="position: absolute; right: 30px;"
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
                    style="display: flex; justify-content: flex-end;"
                >
                    <el-button @click="dialogVisible = false">取 消</el-button>
                    <el-button type="primary" @click="handleConfirm('nodeForm')"
                        >确 定</el-button
                    >
                </span>
            </el-dialog>
        </el-header>

        <el-container>
            <el-aside
                style="width: 250px; margin-top: 10px"
                v-show="addTestActivate"
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
                            :data="dataTree"
                            @node-drag-start="handleDragStart"
                            @node-click="handleNodeClick"
                            @node-drag-end="handleDragEnd"
                            @node-expand="handleNodeExpand"
                            @node-collapse="handleNodeCollapse"
                            node-key="id"
                            draggable
                            highlight-current
                            ref="tree2"
                            :filter-node-method="filterNode"
                            :default-expand-all="false"
                            :expand-on-click-node="false"
                            :default-expanded-keys="expandedNodeIds"
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
                <edit-test
                    v-show="!addTestActivate"
                    :project="$route.params.id"
                    :editBack="editBack"
                    :resetEditTestStepActivate="resetEditTestStepActivate"
                    :node="currentNode.id"
                    :testStepResp="testStepResp"
                    :config="currentConfig"
                    :rigEnv.sync="rigEnv"
                    :tag.sync="tag"
                    :search.sync="search"
                    :addTestActivate="addTestActivate"
                    @addSuccess="handleAddSuccess"
                    @dataChanged="handleContentChange"
                    @showListBtn="ShowListBtnHandle"
                ></edit-test>
                <test-list
                    v-show="addTestActivate"
                    :project="$route.params.id"
                    :pNode="currentNode !== '' ? currentNode.id : ''"
                    :del="del"
                    @testStep="handleTestStep"
                    @resetNode="resetNodeStatus"
                    @refreshTree="getCaseTree"
                    @showListBtn="ShowListBtnHandle"
                    :back="back"
                    :run="run"
                    :move="move"
                    :isSelectCase.sync="isSelectCase"
                    :pageSize.sync="pageSize"
                    :currentPage.sync="currentPage"
                ></test-list>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import TestList from "./components/TestList";
import EditTest from "./components/EditTest";

export default {
    name: "AutoTest",
    components: {
        EditTest,
        TestList
    },
    data() {
        return {
            isShowListBtn: false,
            isContentChanged: false,
            expandedNodeIds: [],
            originalTreeData: [],
            mouseNodeId: -1,
            testStepResp: {},
            nodeForm: {
                name: ""
            },
            rules: {
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
            back: false,
            editBack: false,
            resetEditTestStepActivate: false,
            del: false,
            run: false,
            move: false,
            radio: "根目录",
            addTestActivate: true,
            currentConfig: "",
            treeId: "",
            maxId: "",
            dialogVisible: false,
            currentNode: "",
            data: "",
            filterText: "",
            expand: "&#xe65f;",
            dataTree: [],
            configOptions: [],
            rigEnv: "",
            tag: "",
            search: "",
            pageSize: 10,
            currentPage: 1,
            isSelectCase: false
        };
    },
    computed: {
        buttonActivate: {
            get() {
                return !this.addTestActivate || this.currentNode === "";
            },
            set(value) {
                this.addTestActivate = value;
                this.isShowListBtn = !value;
                this.testStepResp = {};
            }
        }
    },
    watch: {
        filterText(val) {
            this.$refs.tree2.filter(val);
        }
    },
    methods: {
        ShowListBtnHandle(val) {
            this.isShowListBtn = val;
        },
        handleContentChange(hasChanged) {
            this.isContentChanged = hasChanged;
        },
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
        getConfig() {
            this.$api.getAllConfig(this.$route.params.id).then(resp => {
                this.configOptions = resp;
                const _config = this.configOptions.filter(
                    item => item.is_default === true
                );
                if (_config.length) {
                    this.currentConfig = _config[0].name;
                }
            });
        },
        handleAddSuccess() {
            this.addTestActivate = true;
            this.search = "";
            this.pageSize = 10;
            this.currentPage = 1;
            this.testStepResp = {};
            this.back = !this.back;
        },
        closeEditor() {
            this.addTestActivate = true;
            this.isShowListBtn = false;
            this.resetEditTestStepActivate = !this.resetEditTestStepActivate;
            this.editBack = !this.editBack;
        },
        handleBackList() {
            if (this.isContentChanged) {
                this.$confirm("内容未保存，确定关闭？", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                })
                    .then(() => {
                        this.closeEditor();
                    })
                    .catch(() => {});
            } else {
                this.closeEditor();
            }
        },
        handleTestStep(resp) {
            this.testStepResp = resp;
            this.addTestActivate = false;
        },
        getCaseTree() {
            this.$api
                .getTree(this.$route.params.id, { params: { type: 2 } })
                .then(resp => {
                    this.dataTree = resp["tree"];
                    this.treeId = resp["id"];
                    this.maxId = resp["max"];
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
                    type: 2
                })
                .then(resp => {
                    if (resp.success) {
                        this.$message({
                            message: "目录更新成功",
                            type: "success"
                        });
                        this.dataTree = resp.data.tree;
                        this.maxId = resp.data.max;
                    } else {
                        this.$message({
                            message: resp.msg,
                            type: "error"
                        });
                    }
                });
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
                    childNode => childNode.id === this.currentNode.id
                );
                children[index]["label"] = value;
                this.updateTree();
            });
        },
        deleteNode(node) {
            this.$confirm(`删除 ${node.label}, 是否继续?`, "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "warning"
            })
                .then(() => {
                    if (this.currentNode === "") {
                        this.$message.info("请选择一个目录");
                    } else {
                        let dataCopy = JSON.parse(
                            JSON.stringify(this.dataTree)
                        ); // 创建树形数据的拷贝
                        this.removeNodeFromData(this.currentNode.id, dataCopy); // 从拷贝的数据中移除目录
                        this.$api
                            .updateTree(this.treeId, {
                                body: dataCopy, // 发送已经移除目录的数据
                                type: 2
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
                })
                .catch(err => {
                    if (err !== "cancel") {
                        this.$message.error(err);
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
            this.currentNode = node;
            this.data = data;
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        remove(data, node) {
            const parent = node.parent;
            const children = parent.data.children || parent.data;
            const index = children.findIndex(
                childNode => childNode.id === data.id
            );
            children.splice(index, 1);
        },
        append(data) {
            const newChild = {
                id: ++this.maxId,
                label: this.nodeForm.name,
                children: [],
                expand: false // 添加一个 expand 字段到每个目录对象
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
            // 新添加的代码，只有当添加的是子目录时，才把父目录的 id 添加到 expandedKeys 中
            if (this.radio === "子目录") {
                this.expandedNodeIds.push(data.id); // 添加当前父目录的 id
            }
        },
        mouseenter(node) {
            this.mouseNodeId = node.id;
        },
        mouseleave() {
            this.mouseNodeId = -1;
        }
    },
    mounted() {
        this.getCaseTree();
        this.getConfig();
    }
};
</script>

<style scoped>
.icon-group {
    margin-right: 6px;
}

.icon-group i {
    margin-right: 4px;
    padding: 2px;
}
</style>
