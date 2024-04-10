<template>
    <div style="margin-left: -10px">
        <div>
            <div style="display: flex; margin-top: -10px;">
                <el-input
                    style="width: 600px"
                    placeholder="请输入接口名称"
                    v-model.trim="name"
                    clearable
                >
                    <template slot="prepend">接口信息录入</template>
                </el-input>
                <el-button
                    style="margin-left: 10px"
                    slot="append"
                    type="success"
                    @click="save = !save"
                    :disabled="disabledSave"
                    :title="
                        disabledSave ? '不能修改其他人的用例' : '保存用例步骤'
                    "
                    >保存</el-button
                >
                <el-button slot="append" type="danger" @click="handleBack"
                    >返回</el-button
                >
            </div>
            <div>
                <el-input
                    class="input-with-select"
                    placeholder="请输入接口路径或完整的接口地址"
                    v-model.trim="url"
                    clearable
                >
                    <el-select slot="prepend" v-model="method" size="small">
                        <el-option
                            v-for="item of httpOptions"
                            :label="item.label"
                            :value="item.label"
                            :key="item.label"
                        ></el-option>
                    </el-select>
                </el-input>

                <el-tooltip effect="dark" content="循环次数" placement="bottom">
                    <el-input-number
                        v-model="times"
                        controls-position="right"
                        :min="1"
                        :max="100"
                        style="width: 120px"
                    ></el-input-number>
                </el-tooltip>
            </div>
            <el-dialog
                v-if="dialogTableVisible"
                :visible.sync="dialogTableVisible"
                width="70%"
            >
                <report :summary="summary"></report>
            </el-dialog>
        </div>

        <div class="request">
            <el-tabs style="margin-left: 20px" v-model="activeTag">
                <el-tab-pane label="Header" name="first">
                    <span slot="label">
                        Header
                        <el-badge
                            slot="label"
                            :value="
                                handleBadgeValue(response.body.header, 'key')
                            "
                        ></el-badge>
                    </span>
                    <headers
                        :save="save"
                        @dataChanged="handleHeaderContentChange"
                        @header="handleHeader"
                        :header="header"
                    ></headers>
                </el-tab-pane>

                <el-tab-pane label="Request" name="second">
                    <request
                        :save="save"
                        @dataChanged="handleRequestContentChange"
                        @request="handleRequest"
                        :request="request"
                    ></request>
                </el-tab-pane>

                <el-tab-pane label="Extract" name="third">
                    <span slot="label">
                        Extract
                        <el-badge
                            slot="label"
                            :value="
                                handleBadgeValue(response.body.extract, 'key')
                            "
                        ></el-badge>
                    </span>
                    <extract
                        :save="save"
                        @dataChanged="handleExtractContentChange"
                        @extract="handleExtract"
                        :extract="extract"
                    ></extract>
                </el-tab-pane>

                <el-tab-pane label="Validate" name="fourth">
                    <span slot="label">
                        Validate
                        <el-badge
                            slot="label"
                            :value="
                                handleBadgeValue(
                                    response.body.validate,
                                    'actual'
                                )
                            "
                        ></el-badge>
                    </span>
                    <validate
                        :save="save"
                        @dataChanged="handleValidateContentChange"
                        @validate="handleValidate"
                        :validate="validate"
                    ></validate
                ></el-tab-pane>

                <el-tab-pane label="Variables" name="five">
                    <span slot="label">
                        Variables
                        <el-badge
                            slot="label"
                            :value="
                                handleBadgeValue(response.body.variables, 'key')
                            "
                        ></el-badge>
                    </span>
                    <variables
                        :save="save"
                        @dataChanged="handleVariablesContentChange"
                        @variables="handleVariables"
                        :variables="variables"
                    ></variables>
                </el-tab-pane>

                <el-tab-pane label="Hooks" name="six">
                    <span slot="label">
                        Hooks
                        <el-badge
                            slot="label"
                            :value="handleHooksBadge(response.body.hooks)"
                        ></el-badge>
                    </span>
                    <hooks
                        :save="save"
                        @dataChanged="handleHooksContentChange"
                        @hooks="handleHooks"
                        :hooks="hooks"
                    ></hooks>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script>
import Headers from "@/pages/httprunner/components/Headers.vue";
import Request from "@/pages/httprunner/components/Request.vue";
import Extract from "@/pages/httprunner/components/Extract.vue";
import Validate from "@/pages/httprunner/components/Validate.vue";
import Variables from "@/pages/httprunner/components/Variables.vue";
import Hooks from "@/pages/httprunner/components/Hooks.vue";
import Report from "@/pages/reports/DebugReport.vue";
import { isEqual } from "lodash";
export default {
    name: "TestBody",
    components: {
        Headers,
        Request,
        Extract,
        Validate,
        Variables,
        Hooks,
        Report
    },
    props: {
        response: {
            required: true
        },
        disabledSave: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            isOtherContentChanged: false,
            isHeaderContentChanged: false,
            isRequestContentChanged: false,
            isExtractContentChanged: false,
            isValidateContentChanged: false,
            isVariablesContentChanged: false,
            isHooksContentChanged: false,
            loading: false,
            run: false,
            times: this.response.body.times,
            name: this.response.body.name,
            url: this.response.body.url,
            method: this.response.body.method,
            header: [],
            request: [],
            extract: [],
            validate: [],
            variables: [],
            hooks: [],
            tempBody: {},
            save: false,
            summary: {},
            dialogTableVisible: false,
            activeTag: "second",
            httpOptions: [
                {
                    label: "GET"
                },
                {
                    label: "POST"
                },
                {
                    label: "PUT"
                },
                {
                    label: "DELETE"
                },
                {
                    label: "PATCH"
                },
                {
                    label: "HEAD"
                },
                {
                    label: "OPTIONS"
                }
            ]
        };
    },
    watch: {
        name() {
            this.checkForChanges();
        },
        url() {
            this.checkForChanges();
        },
        method() {
            this.checkForChanges();
        },
        times() {
            this.checkForChanges();
        },
        response: {
            deep: true,
            handler() {
                this.setOriginalValues();
                this.id = this.response.id;
                this.name = this.response.body.name;
                this.method = this.response.body.method;
                this.url = this.response.body.url;
                this.times = this.response.body.times;
                this.creator = this.response.creator;
            }
        }
    },
    methods: {
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
        setOriginalValues() {
            if (this.response && this.response.body) {
                this.originalValues = {
                    name: this.response.body.name,
                    url: this.response.body.url,
                    method: this.response.body.method,
                    times: this.response.body.times
                };
            }
        },
        checkForChanges() {
            const currentValues = {
                name: this.name,
                url: this.url,
                method: this.method,
                times: this.times
            };
            this.isOtherContentChanged = !isEqual(
                this.originalValues,
                currentValues
            );
        },
        closeBodyEditor() {
            this.$emit("escEdit");
        },
        handleBack() {
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
                        this.closeBodyEditor();
                    })
                    .catch(() => {});
            } else {
                this.closeBodyEditor();
            }
        },
        handleHeader(header, value) {
            this.header = value;
            this.tempBody.header = header;
        },
        handleRequest(request, value) {
            this.request = value;
            this.tempBody.request = request;
        },
        handleValidate(validate, value) {
            this.validate = value;
            this.tempBody.validate = validate;
        },
        handleExtract(extract, value) {
            this.extract = value;
            this.tempBody.extract = extract;
        },
        handleVariables(variables, value) {
            this.variables = value;
            this.tempBody.variables = variables;
        },
        handleHooks(hooks, value) {
            this.hooks = value;
            this.tempBody.hooks = hooks;
            this.tempBody.url = this.url;
            this.tempBody.method = this.method;
            this.tempBody.name = this.name;
            this.tempBody.times = this.times;

            if (this.validateData()) {
                const body = {
                    header: this.header,
                    request: this.request,
                    extract: this.extract,
                    validate: this.validate,
                    variables: this.variables,
                    hooks: this.hooks,
                    url: this.url,
                    method: this.method,
                    name: this.name,
                    times: this.times
                };
                this.$emit("getNewBody", body, this.tempBody);
                this.run = false;
            }
        },
        // 计算标记的数值
        handleBadgeValue(arr, countKey) {
            let res = 0;
            for (const v of arr) {
                if (v[countKey]) {
                    res += 1;
                }
            }
            return res;
        },
        // 计算hooks的数值
        handleHooksBadge(hook) {
            let res = 0;
            for (const hookElement of hook) {
                if (hookElement["setup"]) {
                    res += 1;
                }
                if (hookElement["teardown"]) {
                    res += 1;
                }
            }
            return res;
        },
        validateData() {
            if (this.name === "") {
                this.$message({
                    type: "warning",
                    message: "接口名称不能为空"
                });
                return false;
            }
            if (this.url === "") {
                this.$message({
                    type: "warning",
                    message: "接口地址不能为空"
                });
                return false;
            }
            return true;
        }
    },
    mounted() {
        this.setOriginalValues();
        this.header = this.response.body.header;
        this.request = this.response.body.request;
        this.extract = this.response.body.extract;
        this.validate = this.response.body.validate;
        this.variables = this.response.body.variables;
        this.hooks = this.response.body.hooks;
    }
};
</script>

<style scoped>
.el-select {
    width: 125px;
}

.input-with-select {
    width: 600px;
    margin-top: 10px;
}

.request {
    margin-top: 15px;
    border: 1px solid #ddd;
}
</style>
