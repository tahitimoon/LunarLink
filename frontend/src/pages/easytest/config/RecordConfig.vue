<template>
    <el-container>
        <el-header style="background: #fff; padding: 0; height: 50px">
            <div class="nav-api-header">
                <div
                    style="display: flex; padding-top: 10px; margin-left: 10px; align-items: center;"
                >
                    <el-button
                        type="primary"
                        size="small"
                        icon="el-icon-circle-plus-outline"
                        @click="addConfig"
                        >新增配置</el-button
                    >
                    <el-button
                        v-if="!addConfigActivate"
                        type="danger"
                        icon="el-icon-delete"
                        size="small"
                        @click="del = !del"
                        :disabled="!isSelectConfig"
                        >批量删除</el-button
                    >
                    <el-button
                        :disabled="!addConfigActivate"
                        type="text"
                        style="position: absolute; right: 30px;"
                        @click="handleBackList"
                        >返回列表</el-button
                    >
                </div>
            </div>
        </el-header>

        <el-container>
            <el-main style="padding: 0; margin-left: 10px">
                <config-body
                    v-show="addConfigActivate"
                    :project="$route.params.id"
                    :response="respConfig"
                    :type="type"
                    @addSuccess="handleAddSuccess"
                ></config-body>
                <config-list
                    v-show="!addConfigActivate"
                    :project="$route.params.id"
                    @respConfig="handleRespConfig"
                    @configDataChanged="handleConfigData"
                    :del="del"
                    :back="back"
                    :page-size.sync="pageSize"
                    :current-page.sync="currentPage"
                    :is-select-config.sync="isSelectConfig"
                ></config-list>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import ConfigBody from "./components/ConfigBody";
import ConfigList from "./components/ConfigList";
export default {
    name: "RecordConfig",
    components: {
        ConfigBody,
        ConfigList
    },
    data() {
        return {
            back: false,
            del: false,
            addConfigActivate: false,
            respConfig: "",
            type: "",
            configData: null,
            isSelectConfig: false,
            pageSize: 10,
            currentPage: 1
        };
    },
    computed: {
        initResponse: {
            get() {
                return this.addConfigActivate;
            },
            set(value) {
                this.addConfigActivate = value;
                this.respConfig = {
                    id: "",
                    name: "",
                    base_url: "",
                    is_default: false,
                    body: {
                        name: "",
                        base_url: "",
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
                        variables: [
                            {
                                key: "",
                                value: "",
                                desc: "",
                                type: 1
                            }
                        ],
                        hooks: [
                            {
                                setup: "",
                                teardown: ""
                            }
                        ],
                        parameters: [
                            {
                                key: "",
                                value: "",
                                desc: ""
                            }
                        ]
                    }
                };
            }
        }
    },
    methods: {
        handleBackList() {
            this.addConfigActivate = false;
            this.respConfig = "";
        },
        handleAddSuccess() {
            this.back = !this.back;
            this.currentPage = 1;
            this.pageSize = 10;
            this.addConfigActivate = false;
        },
        addConfig() {
            this.initResponse = true;
            this.type = "add";
        },
        handleRespConfig(row) {
            this.respConfig = row;
            this.addConfigActivate = true;
            this.type = "edit";
        },
        handleConfigData(data) {
            this.configData = data;
        }
    }
};
</script>

<style scoped></style>
