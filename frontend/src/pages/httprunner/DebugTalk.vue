<template>
    <el-container>
        <el-header style="background-color: #F7F7F7; padding: 0; height: 50px;">
            <div style="display: flex; padding-top: 10px; margin-left: 10px">
                <el-button
                    round
                    type="primary"
                    size="small"
                    icon="el-icon-check"
                    @click="handleConfirm"
                    >点击保存</el-button
                >
                <el-button
                    round
                    icon="el-icon-caret-right"
                    type="info"
                    size="small"
                    @click="handleRunCode"
                    >在线运行</el-button
                >
            </div>
        </el-header>

        <el-main style="padding: 0; margin-left: 10px; overflow: hidden;">
            <MonacoEditor
                ref="editor"
                :height="codeHeight"
                language="python"
                :code="code.code"
                :options="options"
                @mounted="onMounted"
                @codeChange="onCodeChange"
                :key="timeStamp"
            ></MonacoEditor>
        </el-main>
        <el-drawer
            style="margin-top: 100px;"
            :height="codeHeight"
            :destroy-on-close="true"
            :with-header="false"
            :modal="false"
            :visible.sync="isShowDebug"
            size="40%"
        >
            <RunCodeResult :msg="resp.msg"></RunCodeResult>
        </el-drawer>
    </el-container>
</template>

<script>
import MonacoEditor from "vue-monaco-editor";
import RunCodeResult from "./components/RunCodeResult";
// Python代码补全功能-BaseMonacoEditor
import BaseMonacoEditor from "../monaco-editor/BaseMonacoEditor";
export default {
    name: "DebugTalk",
    components: {
        MonacoEditor,
        RunCodeResult,
        BaseMonacoEditor
    },
    data() {
        return {
            editor: null,
            timeStamp: "",
            isShowDebug: false,
            options: {
                selectOnLineNumbers: false,
                scrollbar: {
                    vertical: "hidden",
                    verticalHasArrows: false
                }
            },
            code: {
                code: "",
                id: ""
            },
            resp: {
                msg: ""
            }
        };
    },
    methods: {
        onMounted(editor) {
            this.editor = editor;
        },
        onCodeChange(editor) {
            this.code.code = editor.getValue();
        },
        handleRunCode() {
            this.resp.msg = "";
            this.$api.runDebugtalk(this.code).then(resp => {
                this.resp = resp;
            });
        },
        handleConfirm() {
            this.$api.updateDebugtalk(this.code).then(resp => {
                this.getDebugTalk();
                this.$message.success("代码保存成功");
            });
        },
        getDebugTalk() {
            this.$api.getDebugtalk(this.$route.params.id).then(resp => {
                this.code = resp;
            });
        }
    },
    watch: {
        code() {
            this.timeStamp = new Date().getTime();
        },
        resp() {
            this.isShowDebug = true;
        }
    },
    computed: {
        codeHeight() {
            return window.screen.height - 230;
        }
    },
    mounted() {
        this.getDebugTalk();
    }
};
</script>

<style>
.el-drawer__body {
    overflow: hidden;
}
</style>
