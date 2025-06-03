// 存储应用程序中的数据状态
export default {
    routerName: "",
    projectName: "",
    token: null,
    user: null,
    is_superuser: false,
    show_hosts: false,
    duration: 2000,
    report_path: "/api/easytest/reports/",
    EasyTest: process.env.EASY_TEST_APP_URL, // Renamed key and ENV var reference
    docsURL: process.env.DOCS_URL,
    recordCaseDocsURL: process.env.RECORD_CASE_DOCS_URL
};
