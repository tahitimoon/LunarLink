<template>
    <el-container>
        <el-header style="background: #F7F7F7; padding: 0; height: 50px">
            <div>
                <div
                    style="display: flex; padding-top: 10px; padding-left: 10px"
                >
                    <el-button
                        type="primary"
                        size="small"
                        icon="el-icon-circle-plus"
                        :title="
                            isSuperuser ? '添加项目' : '权限不足, 请联系管理员'
                        "
                        :disabled="!isSuperuser"
                        @click="handleAdd"
                        >添加项目</el-button
                    >
                    <el-button
                        type="success"
                        size="small"
                        icon="el-icon-data-line"
                        @click="dashBoardVisible = true"
                        >项目看板</el-button
                    >
                    <el-button
                        type="info"
                        size="small"
                        icon="el-icon-arrow-left"
                        :disabled="loading || projectData.previous === null"
                        @click="getPagination(projectData.previous)"
                        >上一页</el-button
                    >
                    <el-button
                        type="info"
                        size="small"
                        :disabled="loading || projectData.next === null"
                        @click="getPagination(projectData.next)"
                        >下一页<i
                            class="el-icon-arrow-right el-icon--right"
                        ></i>
                    </el-button>

                    <el-dialog
                        title="添加项目"
                        width="30%"
                        :close-on-click-modal="false"
                        :visible.sync="dialogVisible"
                        :before-close="handleBeforeClose"
                        :style="{ 'text-align': 'center' }"
                    >
                        <el-form
                            :model="projectForm"
                            :rules="rules"
                            ref="projectForm"
                            label-width="150px"
                            class="project"
                        >
                            <el-form-item label="项目名称" prop="name">
                                <el-input
                                    v-model.trim="projectForm.name"
                                    clearable
                                ></el-input>
                            </el-form-item>

                            <el-form-item label="项目描述" prop="desc">
                                <el-input
                                    v-model.trim="projectForm.desc"
                                    clearable
                                ></el-input>
                            </el-form-item>

                            <el-form-item label="负责人" prop="responsible">
                                <el-select
                                    v-model="projectForm.responsible"
                                    placeholder="请选择项目负责人"
                                    filterable
                                    clearable
                                    :style="{ width: '100%' }"
                                >
                                    <el-option
                                        v-for="(item,
                                        index) in responsibleOptions"
                                        :key="index"
                                        :label="item.label"
                                        :value="item.value"
                                    ></el-option>
                                </el-select>
                            </el-form-item>

                            <el-form-item label="YAPI地址" prop="yapi_base_url">
                                <el-input
                                    v-model.trim="projectForm.yapi_base_url"
                                    clearable
                                ></el-input>
                            </el-form-item>

                            <el-form-item
                                label="YAPI token"
                                prop="yapi_openapi_token"
                            >
                                <el-input
                                    v-model.trim="
                                        projectForm.yapi_openapi_token
                                    "
                                    clearable
                                ></el-input>
                            </el-form-item>

                            <!-- TODO: 后面需优化去掉，使用TAPD代替-->
                            <el-form-item
                                label="JIRA bearer token"
                                prop="jira_bearer_token"
                            >
                                <el-input
                                    v-model.trim="projectForm.jira_bearer_token"
                                    clearable
                                ></el-input>
                            </el-form-item>

                            <el-form-item
                                label="JIRA project_key"
                                prop="jira_project_key"
                            >
                                <el-input
                                    v-model.trim="projectForm.jira_project_key"
                                    clearable
                                ></el-input>
                            </el-form-item>
                        </el-form>

                        <span
                            slot="footer"
                            class="dialog-footer"
                            style="display: flex; justify-content: flex-end"
                        >
                            <el-button @click="closeAddDialog('projectForm')"
                                >取 消</el-button
                            >
                            <el-button
                                type="primary"
                                @click="handleConfirm('projectForm')"
                                >确 定</el-button
                            >
                        </span>
                    </el-dialog>

                    <el-dialog
                        title="编辑项目"
                        width="30%"
                        :close-on-click-modal="false"
                        :visible.sync="editVisible"
                        :before-close="handleBeforeClose"
                    >
                        <el-form
                            :model="projectForm"
                            :rules="rules"
                            ref="projectForm"
                            label-width="150px"
                        >
                            <el-form-item label="项目名称" prop="name">
                                <el-input
                                    v-model.trim="projectForm.name"
                                    clearable
                                ></el-input>
                            </el-form-item>
                            <el-form-item label="项目描述" prop="desc">
                                <el-input
                                    v-model.trim="projectForm.desc"
                                    clearable
                                ></el-input>
                            </el-form-item>
                            <el-form-item label="负责人" prop="responsible">
                                <el-select
                                    v-model="projectForm.responsible"
                                    placeholder="请选择项目负责人"
                                    filterable
                                    clearable
                                    :style="{ width: '100%' }"
                                    :disabled="
                                        userName === projectForm.responsible &&
                                            !isSuperuser
                                    "
                                >
                                    <el-option
                                        v-for="(item,
                                        index) in responsibleOptions"
                                        :key="index"
                                        :label="item.label"
                                        :value="item.value"
                                    ></el-option>
                                </el-select>
                            </el-form-item>

                            <el-form-item label="YAPI地址" prop="yapi_base_url">
                                <el-input
                                    v-model.trim="projectForm.yapi_base_url"
                                    clearable
                                >
                                </el-input>
                            </el-form-item>

                            <el-form-item
                                label="YAPI token"
                                prop="yapi_openapi_token"
                            >
                                <el-input
                                    v-model.trim="
                                        projectForm.yapi_openapi_token
                                    "
                                    clearable
                                >
                                </el-input>
                            </el-form-item>

                            <el-form-item
                                label="JIRA bearer token"
                                prop="jira_bearer_token"
                            >
                                <el-input
                                    v-model.trim="projectForm.jira_bearer_token"
                                    clearable
                                >
                                </el-input>
                            </el-form-item>

                            <el-form-item
                                label="JIRA project_key"
                                prop="jira_project_key"
                            >
                                <el-input
                                    v-model.trim="projectForm.jira_project_key"
                                    clearable
                                >
                                </el-input>
                            </el-form-item>
                        </el-form>
                        <span
                            slot="footer"
                            class="dialog-footer"
                            style="display: flex; justify-content: flex-end"
                        >
                            <el-button @click="closeEditDialog('projectForm')"
                                >取 消</el-button
                            >
                            <el-button
                                type="primary"
                                @click="handleConfirm('projectForm')"
                                >确 定</el-button
                            >
                        </span>
                    </el-dialog>
                </div>
            </div>
        </el-header>

        <el-drawer
            :destroy-on-close="true"
            :with-header="false"
            :modal="false"
            size="90%"
            :visible.sync="dashBoardVisible"
        >
            <ProjectDashBoard></ProjectDashBoard>
        </el-drawer>
        <el-container>
            <el-main style="padding: 0; margin-left: 10px">
                <el-table
                    v-loading="loading"
                    highlight-current-row
                    :data="projectData.results"
                    border
                    stripe
                    :show-header="projectData.results.length > 0"
                    style="width: 100%;"
                >
                    <el-table-column
                        label="项目名称"
                        width="250"
                        align="center"
                    >
                        <template v-slot="scope">
                            <span
                                class="cell-ellipsis"
                                style="font-size: 18px; font-weight: bold; cursor:pointer;"
                                @click="handleCellClick(scope.row)"
                                >{{ scope.row.name }}</span
                            >
                        </template>
                    </el-table-column>

                    <el-table-column label="负责人" width="200" align="center">
                        <template v-slot="scope">
                            <span class="cell-ellipsis">{{
                                scope.row.responsible
                            }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column
                        label="项目描述"
                        width="300"
                        align="center"
                    >
                        <template v-slot="scope">
                            <span class="cell-ellipsis">{{
                                scope.row.desc
                            }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column
                        label="创建时间"
                        width="260"
                        align="center"
                    >
                        <template v-slot="scope">
                            <span>{{
                                scope.row.create_time | datetimeFormat
                            }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column label="操作" align="center">
                        <template v-slot="scope">
                            <div
                                style="display: flex; justify-content: center;"
                            >
                                <el-button
                                    size="medium"
                                    @click="handleCellClick(scope.row)"
                                    >进入
                                </el-button>
                                <el-button
                                    size="medium"
                                    type="primary"
                                    :title="
                                        isSuperuser ||
                                        userName === scope.row.responsible
                                            ? '编辑项目'
                                            : '权限不足，请联系管理员'
                                    "
                                    :disabled="
                                        !(
                                            isSuperuser ||
                                            userName === scope.row.responsible
                                        )
                                    "
                                    @click="handleEdit(scope.$index, scope.row)"
                                    >编辑
                                </el-button>
                                <el-button
                                    size="medium"
                                    type="danger"
                                    v-show="isSuperuser"
                                    :title="
                                        isSuperuser
                                            ? '删除项目'
                                            : '权限不足, 请联系管理员'
                                    "
                                    @click="
                                        handleDelete(scope.$index, scope.row)
                                    "
                                    >删除</el-button
                                >
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import ProjectDashBoard from "@/pages/project/ProjectDashBoard.vue";
export default {
    name: "ProjectList",
    components: { ProjectDashBoard },
    data() {
        return {
            isSuperuser: this.$store.state.is_superuser,
            userName: this.$store.state.name,
            dialogVisible: false,
            dashBoardVisible: false,
            editVisible: false,
            projectData: {
                results: []
            },
            projectForm: {
                name: "",
                desc: "",
                responsible: this.$store.state.name,
                id: "",
                yapi_base_url: "",
                yapi_openapi_token: "",
                jira_bearer_token: "",
                jira_project_key: ""
            },
            responsibleOptions: [],
            rules: {
                name: [
                    {
                        required: true,
                        message: "请输入项目名称",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 50,
                        message: "最多不超过50个字符",
                        trigger: "blur"
                    }
                ],
                desc: [
                    {
                        required: true,
                        message: "简要描述下该项目",
                        trigger: "blur"
                    },
                    {
                        min: 1,
                        max: 100,
                        message: "最多不超过100个字符",
                        trigger: "blur"
                    }
                ],
                responsible: [
                    {
                        required: true,
                        message: "请选择项目负责人",
                        trigger: "change"
                    }
                ],
                yapi_base_url: [
                    {
                        required: false,
                        message: "YAPI openapi的url",
                        trigger: "blur"
                    }
                ],
                yapi_openapi_token: [
                    {
                        required: false,
                        message: "YAPI openapi的token",
                        trigger: "blur"
                    }
                ],
                jira_bearer_token: [
                    {
                        required: false,
                        message: "JIRA bearer_token",
                        trigger: "blur"
                    }
                ],
                jira_project_key: [
                    {
                        required: false,
                        message: "jira_project_key",
                        trigger: "blur"
                    }
                ]
            },
            loading: true
        };
    },
    methods: {
        handleCellClick(row) {
            this.$store.commit("setRouterName", "ProjectDetail");
            this.$store.commit("setProjectName", row.name);
            this.setLocalValue("routerName", "ProjectDetail");
            // 在vuex严格模式下, commit会经过mutation函数不会报错, set直接修改会报错
            this.setLocalValue("projectName", row.name);
            this.$router.push({
                name: "ProjectDetail",
                params: { id: row["id"] }
            });
        },
        handleAdd() {
            this.dialogVisible = true;
            this.resetProjectForm();
        },
        handleEdit(index, row) {
            this.editVisible = true;
            this.projectForm.name = row["name"];
            this.projectForm.desc = row["desc"];
            this.projectForm.responsible = row["responsible"];
            this.projectForm.id = row["id"];
            this.projectForm.yapi_base_url = row["yapi_base_url"];
            this.projectForm.yapi_openapi_token = row["yapi_openapi_token"];
            this.projectForm.jira_project_key = row["jira_project_key"];
            this.projectForm.jira_bearer_token = row["jira_bearer_token"];
        },
        handleDelete(index, row) {
            this.$confirm("此操作将永久删除该项目, 是否继续?", "提示", {
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                type: "waring"
            }).then(() => {
                this.$api
                    .deleteProject({ data: { id: row["id"] } })
                    .then(resp => {
                        if (resp["success"]) {
                            this.$message.success(resp.msg);
                            this.getProjectList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
            });
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
        },
        handleConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.dialogVisible = false;
                    this.editVisible = false;
                    let obj;

                    if (this.projectForm.id === "") {
                        obj = this.$api.addProject(this.projectForm);
                    } else {
                        obj = this.$api.updateProject(this.projectForm);
                    }

                    obj.then(resp => {
                        if (resp["success"]) {
                            this.$message.success(resp.msg);
                            this.getProjectList();
                        } else {
                            this.$message.error(resp.msg);
                        }
                        this.resetProjectForm();
                    });
                } else {
                    if (this.projectForm.id !== "") {
                        this.editVisible = true;
                    } else {
                        this.dialogVisible = true;
                    }
                    return false;
                }
            });
        },
        getPagination(url) {
            this.$api.getPagination(url).then(resp => {
                this.projectData = resp;
            });
        },
        getProjectList() {
            this.$api.getProjectList().then(resp => {
                this.projectData = resp;
                this.loading = false;
            });
        },
        resetProjectForm() {
            this.projectForm.name = "";
            this.projectForm.desc = "";
            this.projectForm.responsible = this.$store.state.name;
            this.projectForm.id = "";
            this.projectForm.yapi_base_url = "";
            this.projectForm.yapi_openapi_token = "";
            this.projectForm.jira_bearer_token = "";
            this.projectForm.jira_project_key = "";
        },
        closeEditDialog(formName) {
            this.editVisible = false;
            this.resetForm(formName);
        },
        closeAddDialog(formName) {
            this.dialogVisible = false;
            this.resetForm(formName);
        },
        handleBeforeClose(done) {
            this.resetForm("projectForm");
            done();
        },
        getUserList() {
            this.$api.getUserList().then(resp => {
                for (let i = 0; i < resp.length; i++) {
                    this.responsibleOptions.push({
                        label: resp[i].name,
                        value: resp[i].name
                    });
                }
            });
        }
    },
    created() {
        this.getProjectList();
        this.getUserList();
    }
};
</script>

<style scoped>
.cell-ellipsis {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
