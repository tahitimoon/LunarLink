// 存储应用程序中的数据状态
export default {
    routerName: "",
    projectName: "",
    token: null,
    user: null,
    is_superuser: false,
    show_hosts: false,
    duration: 2000,
    report_path: "/api/lunarlink/reports/",
    LunarLink: process.env.LUNAR_LINK,
    docsURL: process.env.DOCS_URL,
    recordCaseDocsURL: process.env.RECORD_CASE_DOCS_URL
};
