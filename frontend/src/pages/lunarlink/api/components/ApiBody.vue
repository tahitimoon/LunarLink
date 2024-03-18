<template>
    <div class="loading-container">
        <div v-loading="loading">
            <div>
                <div style="display: flex;">
                    <el-input
                        clearable
                        style="width: 600px"
                        placeholder="请输入接口名称"
                        v-model="name"
                    >
                        <template slot="prepend">接口信息录入</template>
                    </el-input>
                    <el-button
                        style="margin-left: 10px"
                        type="primary"
                        @click="reverseStatus"
                        :loading="loading"
                        :disabled="loading"
                        >发送</el-button
                    >
                    <el-button
                        slot="append"
                        type="primary"
                        :title="
                            userName === creator || isSuperuser || !isSaveAs
                                ? '保存'
                                : '只有创建者才能修改'
                        "
                        :disabled="
                            userName !== creator && !isSuperuser && isSaveAs
                        "
                        @click="save = !save"
                        >保存</el-button
                    >
                    <el-button
                        slot="append"
                        type="success"
                        :title="'另存为'"
                        @click="handleSaveAs"
                        >另存为</el-button
                    >
                </div>
                <div>
                    <el-input
                        style="width: 760px; margin-top: 10px"
                        placeholder="请输入接口路径或完整的接口地址"
                        v-model.trim="url"
                        clearable
                    >
                        <el-select
                            style="width: 100px"
                            slot="prepend"
                            v-model="method"
                        >
                            <el-option
                                v-for="item of httpOptions"
                                :label="item.label"
                                :value="item.label"
                                :key="item.value"
                            ></el-option>
                        </el-select>
                        <template slot="prepend">
                            <span style="margin-left: 20px">{{
                                config.base_url
                            }}</span>
                        </template>
                    </el-input>

                    <el-tooltip
                        effect="dark"
                        content="循环次数"
                        placement="bottom"
                    >
                        <el-input-number
                            v-model="times"
                            controls-position="right"
                            :min="1"
                            :max="100"
                            style="width: 120px"
                        ></el-input-number>
                    </el-tooltip>
                </div>
            </div>
            <div class="request">
                <el-dialog
                    v-if="dialogTableVisible"
                    :visible.sync="dialogTableVisible"
                    width="70%"
                >
                    <report :summary="summary"></report>
                </el-dialog>

                <el-tabs style="margin-left: 20px" v-model="activeTag">
                    <el-tab-pane label="Header" name="first">
                        <span slot="label">
                            Header
                            <el-badge
                                slot="label"
                                :value="
                                    handleBadgeValue(
                                        response ? response.body.header : [],
                                        'key'
                                    )
                                "
                            ></el-badge>
                        </span>
                        <headers
                            :save="save"
                            @header="handleHeader"
                            @dataChanged="handleHeaderDataChange"
                            :header="response ? response.body.header : []"
                        ></headers>
                    </el-tab-pane>

                    <el-tab-pane label="Request" name="second">
                        <request
                            :save="save"
                            :resetDataType="resetFlag"
                            @request="handleRequest"
                            @dataChanged="handleRequestDataChange"
                            :request="response ? response.body.request : []"
                        ></request>
                    </el-tab-pane>

                    <el-tab-pane label="Extract" name="third">
                        <span slot="label">
                            Extract
                            <el-badge
                                slot="label"
                                :value="
                                    handleBadgeValue(
                                        response ? response.body.extract : [],
                                        'key'
                                    )
                                "
                            ></el-badge>
                        </span>
                        <extract
                            :save="save"
                            @extract="handleExtract"
                            @dataChanged="handleExtractDataChange"
                            :extract="response ? response.body.extract : []"
                        ></extract>
                    </el-tab-pane>

                    <el-tab-pane label="Validate" name="fourth">
                        <span slot="label">
                            Validate
                            <el-badge
                                slot="label"
                                :value="
                                    handleBadgeValue(
                                        response ? response.body.validate : [],
                                        'actual'
                                    )
                                "
                            ></el-badge>
                        </span>
                        <validate
                            :save="save"
                            @validate="handleValidate"
                            @dataChanged="handleValidateDataChange"
                            :validate="response ? response.body.validate : []"
                        ></validate>
                    </el-tab-pane>

                    <el-tab-pane label="Variables" name="five">
                        <span slot="label">
                            Variables
                            <el-badge
                                slot="label"
                                :value="
                                    handleBadgeValue(
                                        response ? response.body.variables : [],
                                        'key'
                                    )
                                "
                            ></el-badge>
                        </span>
                        <variables
                            :save="save"
                            @variables="handleVariables"
                            @dataChanged="handleVariablesDataChange"
                            :variables="response ? response.body.variables : []"
                        ></variables>
                    </el-tab-pane>

                    <el-tab-pane label="Hooks" name="six">
                        <span slot="label">
                            Hooks
                            <el-badge
                                slot="label"
                                :value="
                                    handleHooksBadge(
                                        response ? response.body.hooks : []
                                    )
                                "
                            ></el-badge>
                        </span>
                        <hooks
                            :save="save"
                            @hooks="handleHooks"
                            @dataChanged="handleHooksDataChange"
                            :hooks="response ? response.body.hooks : []"
                        ></hooks>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </div>
        <el-button
            v-if="showCancel"
            @click="cancelRequest"
            class="custom-button"
            size="mini"
            >取消</el-button
        >
    </div>
</template>

<script>
import Headers from "@/pages/httprunner/components/Headers";
import Request from "@/pages/httprunner/components/Request";
import Extract from "@/pages/httprunner/components/Extract";
import Validate from "@/pages/httprunner/components/Validate";
import Variables from "@/pages/httprunner/components/Variables";
import Hooks from "@/pages/httprunner/components/Hooks";
import Report from "@/pages/reports/DebugReport";
import axios from "axios";
import { isEqual } from "lodash";

export default {
    name: "ApiBody",
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
        host: {
            required: false
        },
        nodeId: {
            required: false
        },
        project: {
            required: false
        },
        config: {
            required: false
        },
        response: {
            required: false
        },
        isSaveAs: Boolean
    },
    data() {
        return {
            originalValues: {
                name: "",
                url: "",
                method: "",
                times: 1
            },
            isSuperuser: this.$store.state.is_superuser,
            userName: this.$store.state.name,
            loading: false,
            showCancel: false, // 用于控制取消按钮的显示
            times: 1,
            name: "",
            url: "",
            id: "",
            creator: "",
            header: [],
            request: [],
            extract: [],
            validate: [],
            variables: [],
            hooks: [],
            method: "GET",
            dialogTableVisible: false,
            resetFlag: false, // 重置子组件dataType
            save: false,
            run: false,
            summary: {},
            activeTag: "second",
            httpOptions: [
                {
                    label: "GET",
                    value: 1
                },
                {
                    label: "POST",
                    value: 2
                },
                {
                    label: "PUT",
                    value: 3
                },
                {
                    label: "DELETE",
                    value: 4
                },
                {
                    label: "PATCH",
                    value: 5
                },
                {
                    label: "HEAD",
                    value: 6
                },
                {
                    label: "OPTIONS",
                    value: 7
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
        handleHeaderDataChange(hasChanged) {
            this.$emit("headerContentChanged", hasChanged);
        },
        handleRequestDataChange(hasChanged) {
            this.$emit("requestContentChanged", hasChanged);
        },
        handleExtractDataChange(hasChanged) {
            this.$emit("extractContentChanged", hasChanged);
        },
        handleValidateDataChange(hasChanged) {
            this.$emit("validateContentChanged", hasChanged);
        },
        handleVariablesDataChange(hasChanged) {
            this.$emit("variablesContentChanged", hasChanged);
        },
        handleHooksDataChange(hasChanged) {
            this.$emit("hooksContentChanged", hasChanged);
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
            const hasChanged = !isEqual(this.originalValues, currentValues);
            this.$emit("otherContentChanged", hasChanged);
        },
        resetTabsState() {
            this.activeTag = "second";
        },
        reverseStatus() {
            this.save = !this.save;
            this.run = true;
        },
        handleHeader(header) {
            this.header = header;
        },
        handleRequest(request) {
            this.request = request;
        },
        handleValidate(validate) {
            this.validate = validate;
        },
        handleExtract(extract) {
            this.extract = extract;
        },
        handleVariables(variables) {
            this.variables = variables;
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
                if (hookElement.setup) {
                    res += 1;
                }
                if (hookElement.teardown) {
                    res += 1;
                }
            }
            return res;
        },
        // 当save值变化时触发
        handleHooks(hooks) {
            this.hooks = hooks;
            if (!this.run) {
                if (this.id === "") {
                    this.addAPI();
                } else {
                    this.updateAPI();
                }
            } else {
                this.runAPI();
                this.run = false;
            }
        },
        handleSaveAs() {
            this.save = !this.save;
            this.id = "";
        },
        addAPI() {
            if (this.validateData()) {
                this.$api
                    .addAPI({
                        header: this.header,
                        request: this.request,
                        extract: this.extract,
                        validate: this.validate,
                        variables: this.variables,
                        hooks: this.hooks,
                        name: this.name,
                        url: this.url,
                        method: this.method,
                        times: this.times,
                        // 另存为时，使用response的值
                        nodeId: this.response.relation || this.nodeId,
                        project: this.response.project || this.project
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$emit("addSuccess");
                            this.$emit("refreshTree");
                            this.$message.success(resp.msg);
                        } else {
                            this.$message.error({
                                message: resp.msg,
                                duration: this.$store.state.duration
                            });
                        }
                        this.resetTabsState();
                        this.resetFlag = !this.resetFlag;
                    });
            }
        },
        updateAPI() {
            if (this.validateData()) {
                this.$api
                    .updateAPI(this.id, {
                        header: this.header,
                        request: this.request,
                        extract: this.extract,
                        validate: this.validate,
                        variables: this.variables,
                        hooks: this.hooks,
                        name: this.name,
                        url: this.url,
                        method: this.method,
                        times: this.times
                    })
                    .then(resp => {
                        if (resp.success) {
                            this.$emit("addSuccess");
                            this.$message.success(resp.msg);
                        } else {
                            this.$message.error({
                                message: resp.msg,
                                duration: this.$store.state.duration
                            });
                        }
                        this.resetTabsState();
                        this.resetFlag = !this.resetFlag;
                    });
            }
        },
        runAPI() {
            if (this.validateData()) {
                const isUrlValid =
                    this.url.startsWith("http://") ||
                    this.url.startsWith("https://");
                if (!isUrlValid && !this.config.name) {
                    this.$message({
                        type: "warning",
                        message: "请先选择配置"
                    });
                    return false;
                } else {
                    this.loading = true;
                    this.showCancel = true;

                    // 创建 cancel token
                    this.cancelTokenSource = axios.CancelToken.source();

                    // 设置一个定时器，2分钟后执行
                    const timeout = setTimeout(() => {
                        this.apiRunning = false;
                        this.cancelTokenSource.cancel("Request timed out");
                    }, 120000); // 120000ms equals to 2 minutes

                    this.$api
                        .runSingleAPI(
                            {
                                header: this.header,
                                request: this.request,
                                extract: this.extract,
                                validate: this.validate,
                                variables: this.variables,
                                hooks: this.hooks,
                                name: this.name,
                                url: this.url,
                                method: this.method,
                                times: this.times,
                                project: this.project,
                                config: this.config.name,
                                host: this.host
                            },
                            this.cancelTokenSource.token
                        )
                        .then(resp => {
                            clearTimeout(timeout); // 清除定时器
                            this.summary = resp;
                            this.dialogTableVisible = true;
                            this.loading = false;
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
            }
        },
        cancelRequest() {
            this.loading = false; // 关闭Loading
            this.showCancel = false; // 隐藏‘取消请求’按钮
            this.cancelTokenSource.cancel("User cancelled the request"); // 取消请求
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
    }
};
</script>
<style scoped>
.request {
    margin-top: 15px;
    border: 1px solid #ddd;
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
    margin-left: 10px;
}
</style>
