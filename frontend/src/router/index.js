import Vue from "vue";
import Router from "vue-router";
import Login from "@/pages/login/Login";
import LoginLog from "@/pages/login/LoginLog";
import Logging from "@/pages/login/Logging";
import Home from "@/pages/home/Home";
import ProjectList from "@/pages/project/ProjectList";
import ProjectDetail from "@/pages/project/ProjectDetail";
import DebugTalk from "@/pages/httprunner/DebugTalk";
import RecordApi from "@/pages/lunarlink/api/RecordApi";
import RecordConfig from "@/pages/lunarlink/config/RecordConfig";
import TestCase from "@/pages/lunarlink/case/TestCase";
import AutoTest from "@/pages/lunarlink/case/AutoTest";
import RecordCase from "@/pages/lunarlink/case/RecordCase";
import GlobalEnv from "@/pages/variables/GlobalEnv";
import Tasks from "@/pages/task/Tasks";
import ReportList from "@/pages/reports/ReportList";

Vue.use(Router);

export default new Router({
    mode: "history",
    routes: [
        {
            path: "/",
            redirect: "/lunarlink/login"
        },
        {
            path: "/lunarlink/login",
            name: "Login",
            component: Login,
            meta: {
                title: "LunarLink测试平台"
            }
        },
        {
            path: "/lunarlink",
            name: "Index",
            component: Home,
            meta: {
                title: "首页",
                requireAuth: true
            },
            children: [
                {
                    name: "ProjectList",
                    path: "project_list",
                    component: ProjectList,
                    meta: {
                        title: "项目列表",
                        requireAuth: true
                    }
                },
                {
                    name: "ProjectDetail",
                    path: "project/:id/dashbord",
                    component: ProjectDetail,
                    meta: {
                        title: "项目预览",
                        requireAuth: true
                    }
                },
                {
                    name: "RecordApi",
                    path: "api_record/:id",
                    component: RecordApi,
                    meta: {
                        title: "接口管理",
                        requireAuth: true
                    }
                },
                {
                    name: "RecordConfig",
                    path: "record_config/:id",
                    component: RecordConfig,
                    meta: {
                        title: "配置管理",
                        requireAuth: true
                    }
                },
                {
                    name: "TestCase",
                    path: "test_case/:id",
                    component: TestCase,
                    meta: {
                        title: "测试用例",
                        requireAuth: true
                    },
                    children: [
                        {
                            name: "AutoTest",
                            path: "auto_test",
                            component: AutoTest,
                            meta: {
                                title: "添加用例",
                                requireAuth: true
                            }
                        },
                        {
                            name: "RecordCase",
                            path: "record_case",
                            component: RecordCase,
                            meta: {
                                title: "录制用例",
                                requireAuth: true
                            }
                        }
                    ]
                },
                {
                    name: "GlobalEnv",
                    path: "global_env/:id",
                    component: GlobalEnv,
                    meta: {
                        title: "全局变量",
                        requireAuth: true
                    }
                },
                {
                    name: "DebugTalk",
                    path: "debugtalk/:id",
                    component: DebugTalk,
                    meta: {
                        title: "驱动代码",
                        requireAuth: true
                    }
                },
                {
                    name: "Tasks",
                    path: "tasks/:id",
                    component: Tasks,
                    meta: {
                        title: "定时任务",
                        requireAuth: true
                    }
                },
                {
                    name: "Reports",
                    path: "reports/:id",
                    component: ReportList,
                    meta: {
                        title: "测试报告",
                        requireAuth: true
                    }
                },
                {
                    name: "Logging",
                    path: "logging/:id",
                    component: Logging,
                    meta: {
                        title: "日志管理",
                        requireAuth: true
                    },
                    children: [
                        {
                            name: "LoginLog",
                            path: "login_log",
                            component: LoginLog,
                            meta: {
                                title: "登录日志",
                                requireAuth: true
                            }
                        }
                    ]
                }
            ]
        }
    ]
});
