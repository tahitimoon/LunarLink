"use strict";
// 开发环境的环境变量配置
const EasyTest = process.env.EASY_TEST_APP_URL || "EasyTest";
module.exports = {
    NODE_ENV: '"development"',
    DOCS_URL: '"https://easy-test-docs.fun/docs/guide/introduce.html"',
    EASY_TEST_APP_URL: "'" + EasyTest + "'",
    RECORD_CASE_DOCS_URL:
        '"https://easy-test-docs.fun/docs/guide/test_case.html"',
    VUE_APP_BASE_URL: '"http://127.0.0.1:8000"' // 本地开发环境后端服务器地址
};
