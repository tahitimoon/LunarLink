# -*- coding: utf-8 -*-
"""
@File    : urls.py
@Time    : 2023/1/14 11:23
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

from django.urls import path
from lunarlink.views import (
    api,
    ci,
    config,
    debugtalk,
    project,
    report,
    run,
    schedule,
    suite,
    yapi,
    variables,
)


urlpatterns = [
    # 访问统计相关接口
    path(
        "visit",
        project.VisitView.as_view({"get": "list"}),
    ),
    # 项目相关接口
    path(
        "project",
        project.ProjectView.as_view(
            {
                "get": "list",
                "post": "add",
                "patch": "update",
                "delete": "delete",
            }
        ),
    ),
    path("project/<int:pk>", project.ProjectView.as_view({"get": "single"})),
    path("project/yapi/<int:pk>", project.ProjectView.as_view({"get": "yapi_info"})),
    path("dashboard", project.DashBoardView.as_view()),
    # 二叉树接口
    path("tree/<int:pk>", project.TreeView.as_view()),
    # 导入yapi
    path("yapi/<int:pk>", yapi.YAPIView.as_view()),
    # api模板
    path(
        "api",
        api.APITemplateView.as_view(
            {
                "post": "add",
                "get": "list",
                "delete": "bulk_destroy",
            }
        ),
    ),
    path(
        "api/<int:pk>",
        api.APITemplateView.as_view(
            {
                "delete": "destroy",
                "patch": "update",
                "post": "copy",
                "get": "single",
            }
        ),
    ),
    path(
        "api/move_api",
        api.APITemplateView.as_view({"patch": "move"}),  # api修改relation所属目录
    ),
    path(
        "api/tag",
        api.APITemplateView.as_view({"patch": "add_tag"}),  # api修改状态
    ),
    path(
        "api/sync/<int:pk>",
        api.APITemplateView.as_view({"patch": "sync_case"}),  # api同步测试用例
    ),
    # 测试用例
    path(
        "test",
        suite.TestCaseView.as_view(
            {
                "get": "get",
                "post": "post",
                "delete": "bulk_destroy",
            }
        ),
    ),
    path(
        "test/<int:pk>",
        suite.TestCaseView.as_view(
            {
                # 如果请求方法和处理方法同名时可以省略
                "post": "copy",
                "delete": "destroy",
                "put": "put",
                "patch": "patch",
            }
        ),
    ),
    path(
        "test/move_case",
        suite.TestCaseView.as_view({"patch": "move"}),  # case修改relation
    ),
    path(
        "test/tag",
        suite.TestCaseView.as_view({"patch": "update_tag"}),
    ),
    path("teststep/<int:pk>", suite.CaseStepView.as_view()),
    # 用例录制
    path("record/start", suite.RecordStartView.as_view(), name="record_start"),
    path("record/stop", suite.RecordStopView.as_view(), name="record_stop"),
    path("record/status", suite.RecordStatusView.as_view(), name="record_status"),
    path("record/remove", suite.RecordRemoveView.as_view(), name="record_remove"),
    path("record_case", suite.GenerateCaseView.as_view(), name="generate_case"),
    # run api 运行API
    path("run_api_pk/<int:pk>", run.run_api_pk),
    path("run_api", run.run_api),
    # run testsuite 运行测试用例集
    path("run_testsuite", run.run_testsuite),
    path("run_testsuite_pk/<int:pk>", run.run_testsuite_pk),
    path("run_test", run.run_test),
    path("run_suite_tree", run.run_suite_tree),
    path("run_multi_tests", run.run_multi_tests),
    # config-配置管理
    path(
        "config",
        config.ConfigView.as_view(
            {
                "post": "add",
                "get": "list",
                "delete": "bulk_destroy",
            }
        ),
    ),
    path(
        "config/<int:pk>",
        config.ConfigView.as_view(
            {
                "patch": "update",
                "post": "copy",
                "delete": "destroy",
                "get": "all",
            }
        ),
    ),
    # 全局变量
    path(
        "variables",
        variables.VariablesView.as_view(
            {
                "get": "list",
                "post": "add",
                "delete": "bulk_destroy",
            }
        ),
    ),
    path(
        "variables/<int:pk>",
        variables.VariablesView.as_view(
            {
                "patch": "update",
                "delete": "destroy",
            }
        ),
    ),
    # debugtalk.py相关接口
    path("debugtalk/<int:pk>", debugtalk.DebugTalkView.as_view({"get": "debugtalk"})),
    path(
        "debugtalk",
        debugtalk.DebugTalkView.as_view(
            {
                "patch": "update",
                "post": "run",
            }
        ),
    ),
    # 历史报告
    path(
        "reports",
        report.ReportView.as_view(
            {
                "get": "list",
                "delete": "bulk_destroy",
            }
        ),
    ),
    path(
        "reports/<int:pk>",
        report.ReportView.as_view(
            {
                "delete": "destroy",
                "get": "look",
            }
        ),
    ),
    # 定时任务相关接口
    path(
        "schedule",
        schedule.ScheduleView.as_view(
            {
                "get": "list",
                "post": "add",
            }
        ),
    ),
    path(
        "schedule/<int:pk>",
        schedule.ScheduleView.as_view(
            {
                "get": "run",
                "put": "update",
                "patch": "patch",
                "delete": "delete",
                "post": "copy",
            }
        ),
    ),
    # gitlab-ci, 当前暂未用到
    path(
        "gitlab-ci/",
        ci.CIView.as_view(
            {
                "post": "run_ci_tests",
                "get": "get_ci_report_url",
            }
        ),
    ),
]
