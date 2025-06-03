"use strict";
// 生产环境的环境变量配置
const EasyTest = process.env.EASY_TEST_APP_URL || "EasyTest";
module.exports = {
    NODE_ENV: '"production"',
    DOCS_URL: '"https://easy-test-docs.fun/docs/guide/introduce.html"',
    EASY_TEST_APP_URL: "'" + EasyTest + "'",
    RECORD_CASE_DOCS_URL:
        '"https://easy-test-docs.fun/docs/guide/test_case.html"',
    VUE_APP_BASE_URL: '""'
};
