<template>
    <MonacoEditor
        :height="codeHeight"
        language="text"
        :code="msg"
        :options="options"
    >
    </MonacoEditor>
</template>

<script>
import MonacoEditor from "vue-monaco-editor";
export default {
    name: "RunCodeResult",
    components: {
        MonacoEditor
    },
    props: {
        msg: {
            required: true
        }
    },
    data() {
        return {
            options: {
                selectOnLineNumbers: false,
                readOnly: true,
                scrollbar: {
                    vertical: "hidden",
                    verticalHasArrows: false
                }
            }
        };
    },
    computed: {
        codeHeight() {
            return window.screen.height - 230;
        }
    }
};
</script>

<style scoped></style>
