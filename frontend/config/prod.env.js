"use strict";
// 生产环境的环境变量配置
const LunarLink = process.env.LUNAR_LINK || "LunarLink";
module.exports = {
    NODE_ENV: '"production"',
    DOCS_URL: '"https://lunarlink-doc.vercel.app/docs/guide/introduce.html"',
    LUNAR_LINK: "'" + LunarLink + "'",
    RECORD_CASE_DOCS_URL:
        '"https://lunarlink-doc.vercel.app/docs/guide/test_case.html"',
    VUE_APP_BASE_URL: '""'
};
