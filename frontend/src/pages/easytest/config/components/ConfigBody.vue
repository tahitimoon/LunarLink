<template>
    <div>
        <div style="margin-top: 10px;">
            <el-input
                style="width: 600px"
                placeholder="请输入配置名称"
                v-model.trim="name"
                clearable
            >
                <template slot="prepend">配置信息录入</template>
                <el-button
                    slot="append"
                    type="success"
                    plain
                    @click="save = !save"
                    >保存</el-button
                >
            </el-input>
        </div>
        <div>
            <el-input
                class="input-with-select"
                placeholder="请输入 base_url 地址"
                v-model.trim="baseUrl"
                clearable
            >
                <template slot="prepend">配置请求地址</template>
            </el-input>
        </div>
        <div>
            <el-switch
                style="display: block; margin-top: 10px"
                v-model="is_default"
                active-color="#13ce66"
                :disabled="isAddConfig"
                active-text="默认配置"
            ></el-switch>
        </div>
        <div class="request">
            <el-tabs v-model="activeTag" style="margin-left: 20px">
                <el-tab-pane label="Header" name="first">
                    <headers
                        :save="save"
                        @header="handleHeader"
                        :header="response ? response.body.header : []"
                    ></headers>
                </el-tab-pane>

                <el-tab-pane label="Variables" name="third">
                    <variables
                        :save="save"
                        @variables="handleVariables"
                        :variables="response ? response.body.variables : []"
                    ></variables>
                </el-tab-pane>
                <!--TODO: 配置管理里面的前置hooks配置后，执行API会找不到request-->
                <el-tab-pane label="Hooks" name="fourth">
                    <hooks
                        :save="save"
                        @hooks="handleHooks"
                        :hooks="response ? response.body.hooks : []"
                    ></hooks>
                </el-tab-pane>

                <el-tab-pane label="Parameters" name="five">
                    <parameters
                        :save="save"
                        @parameters="handleParameters"
                        :parameters="response ? response.body.parameters : []"
                    ></parameters>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script>
import Headers from "@/pages/httprunner/components/Headers";
import Variables from "@/pages/httprunner/components/Variables";
import Hooks from "@/pages/httprunner/components/Hooks";
import Parameters from "@/pages/httprunner/components/Parameters";

export default {
    name: "ConfigBody",
    components: {
        Headers,
        Variables,
        Hooks,
        Parameters
    },
    data() {
        return {
            name: "",
            baseUrl: "",
            is_default: false,
            id: "",
            header: [],
            request: [],
            variables: [],
            hooks: [],
            parameters: [],
            save: false,
            activeTag: "third"
        };
    },
    props: {
        project: {
            required: false
        },
        response: {
            required: false
        },
        type: {
            type: String,
            default: ""
        }
    },
    computed: {
        isAddConfig() {
            return this.type === "add";
        }
    },
    watch: {
        response() {
            this.name = this.response.name;
            this.baseUrl = this.response.base_url;
            this.id = this.response.id;
            this.is_default = this.response.is_default;
        }
    },
    methods: {
        handleHeader(header) {
            this.header = header;
        },
        handleVariables(variables) {
            this.variables = variables;
        },
        handleHooks(hooks) {
            this.hooks = hooks;
        },
        handleParameters(parameters) {
            this.parameters = parameters;
            if (this.id === "") {
                this.addConfig();
            } else {
                this.updateConfig();
            }
        },
        addConfig() {
            if (this.variableData()) {
                this.$api
                    .addConfig({
                        parameters: this.parameters,
                        header: this.header,
                        request: this.request,
                        variables: this.variables,
                        hooks: this.hooks,
                        base_url: this.baseUrl,
                        name: this.name,
                        project: this.project,
                        is_default: this.is_default
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message.success({
                                message: "配置添加成功",
                                duration: this.$store.state.duration
                            });
                            this.$emit("addSuccess");
                        } else {
                            this.$message.error({
                                message: resp.msg,
                                duration: this.$store.state.duration
                            });
                        }
                    });
            }
        },
        updateConfig() {
            if (this.variableData()) {
                this.$api
                    .updateConfig(this.id, {
                        parameters: this.parameters,
                        header: this.header,
                        request: this.request,
                        variables: this.variables,
                        hooks: this.hooks,
                        base_url: this.baseUrl,
                        name: this.name,
                        is_default: this.is_default
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$message.success(resp.msg);
                            this.$emit("addSuccess");
                        } else {
                            this.$message.error(resp.msg);
                        }
                    });
            }
        },
        variableData() {
            if (this.name === "") {
                this.$message.error("配置名称不能为空");
                return false;
            }
            return true;
        }
    }
};
</script>

<style scoped>
.input-with-select {
    width: 600px;
    margin-top: 10px;
}

.request {
    margin-top: 15px;
    border: 1px solid #ddd;
}
</style>
