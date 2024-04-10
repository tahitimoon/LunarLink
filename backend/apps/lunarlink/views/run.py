# -*- coding: utf-8 -*-
"""
@File    : run.py
@Time    : 2023/2/6 10:51
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 运行API
"""
import logging
from ast import literal_eval

from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from lunarlink.utils import loader, response
from lunarlink import tasks
from lunarlink.utils.decorator import request_log
from lunarlink.utils.host import parse_host
from lunarlink.utils.parser import Format
from lunarlink import models
from apps.exceptions.error import (
    ApiNotFound,
    ConfigNotFound,
    CaseStepNotFound,
)

logger = logging.getLogger(__name__)

"""运行方式
"""

config_err = {
    "success": False,
    "msg": "指定的配置文件不存在",
    "code": "9999",
}


@api_view(["GET"])
@request_log(level="INFO")
def run_api_pk(request, pk):
    """
    运行单个接口
    """
    config_name = request.query_params.get("config", "请选择")
    try:
        api = models.API.objects.get(id=pk)
    except ObjectDoesNotExist:
        return Response(response.API_NOT_FOUND)

    config = (
        None
        if config_name == "请选择"
        else literal_eval(
            models.Config.objects.get(name=config_name, project=api.project).body
        )
    )

    summary = loader.debug_api(
        api=literal_eval(api.body),
        project=api.project.id,
        name=api.name,
        config=config,
        user=request.user.id,
    )

    return Response(summary)


@api_view(["POST"])
@request_log(level="INFO")
def run_api(request):
    """run api by body"""

    config_name = request.data.pop("config", "请选择")

    api = Format(request.data)
    api.parse()

    config = None
    if config_name != "请选择":
        try:
            config = literal_eval(
                models.Config.objects.get(
                    name=config_name, project__id=api.project
                ).body
            )
        except ObjectDoesNotExist:
            logger.error(f"指定配置文件不存在:{config_name}")
            return Response(config_err)

    summary = loader.debug_api(
        api=api.testcase,
        project=api.project,
        name=api.name,
        config=config,
        user=request.user.id,
    )

    return Response(summary)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "project",
            openapi.IN_QUERY,
            description="project id",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "name",
            openapi.IN_QUERY,
            description="case name",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "host",
            openapi.IN_QUERY,
            description="host",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "async",
            openapi.IN_QUERY,
            description="async",
            type=openapi.TYPE_STRING,
        ),
    ],
    operation_summary="执行单个测试用例集",
)
@api_view(["GET"])
@request_log(level="INFO")
def run_testsuite_pk(request, **kwargs):
    """
    执行测试用例集

    URL参数 query string:
        project
        name
        host
    """

    pk = kwargs.get("pk")

    test_list = (
        models.CaseStep.objects.filter(case__id=pk).order_by("step").values("body")
    )

    project = request.query_params["project"]
    name = request.query_params["name"]
    host = request.query_params["host"]
    back_async = request.query_params.get("async", False)

    test_case = []
    config = None

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    for content in test_list:
        body = literal_eval(content["body"])
        if "base_url" in body["request"].keys():
            try:
                config = literal_eval(
                    models.Config.objects.get(
                        name=body["name"], project__id=project
                    ).body
                )
            except ObjectDoesNotExist:
                return Response(response.CONFIG_NOT_EXISTS)
            else:
                continue

        test_case.append(parse_host(ip=host, api=body))

    # 异步执行
    if back_async:
        tasks.async_debug_api.delay(
            api=test_case,
            project=project,
            name=name,
            config=parse_host(ip=host, api=config),
            user=request.user.id,
        )
        summary = response.TASK_RUN_SUCCESS
    else:  # 同步
        summary = loader.debug_api(
            api=test_case,
            project=project,
            name=name,
            config=parse_host(ip=host, api=config),
            user=request.user.id,
        )

    return Response(summary)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            "body",
            "project",
            "name",
            "host",
        ],
        properties={
            "body": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                ),
                description="body",
            ),
            "project": openapi.Schema(type=openapi.TYPE_INTEGER, description="project"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="name"),
            "host": openapi.Schema(type=openapi.TYPE_STRING, description="host"),
        },
    ),
)
@api_view(["POST"])
@request_log(level="INFO")
def run_testsuite(request):
    """
    调式测试用例集
    {
        name: str,
        body: dict,
        host: str,
        project: int,
    }
    """
    try:
        body = request.data["body"]
        project = request.data["project"]
        name = request.data["name"]
        host = request.data["host"]
    except ObjectDoesNotExist:
        return Response(response.KEY_MISS)

    test_case = []
    config = None

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    for test in body:
        try:
            test = loader.load_test(test=test, project=project)
        except ConfigNotFound:
            return Response(response.CONFIG_NOT_EXISTS)
        except ApiNotFound:
            return Response(response.API_NOT_FOUND)
        except CaseStepNotFound:
            return Response(response.CASE_STEP_NOT_EXIST)
        if "base_url" in test["request"].keys():
            config = test
            continue

        test_case.append(parse_host(ip=host, api=test))

    summary = loader.debug_api(
        api=test_case,
        project=project,
        name=name,
        config=parse_host(ip=host, api=config),
        user=request.user.id,
    )

    return Response(summary)


@api_view(["POST"])
@request_log(level="INFO")
def run_test(request):
    """
    测试用例中调式单个接口

    入参:
    {
        host: str,
        body: dict,
        project: int,
        config: null or dict,
    }
    """
    body = request.data.get("body")
    config = request.data.get("config", None)
    project = request.data.get("project")
    host = request.data.get("host")

    if host != "请选择":
        try:
            host = models.HostIP.objects.get(
                name=host, project=project
            ).value.splitlines()
        except ObjectDoesNotExist:
            return Response(response.HOSTIP_NOT_EXISTS)

    if config:
        try:
            config_obj = models.Config.objects.get(project=project, name=config["name"])
        except ObjectDoesNotExist:
            return Response(response.CONFIG_NOT_EXISTS)
        config = literal_eval(config_obj.body)

    try:
        test = loader.load_test(test=body)
    except ConfigNotFound:
        return Response(response.CONFIG_NOT_EXISTS)
    except ApiNotFound:
        return Response(response.API_NOT_FOUND)
    except CaseStepNotFound:
        return Response(response.CASE_STEP_NOT_EXIST)

    summary = loader.debug_api(
        api=parse_host(ip=host, api=test),
        project=project,
        name=body.get("name", None),
        config=parse_host(ip=host, api=config),
        user=request.user.id,
    )

    return Response(summary)


@api_view(["POST"])
@request_log(level="INFO")
def run_suite_tree(request):
    """
    选择目录节点执行用例集

    {
        project: int
        relation: list
        name: str
        async: bool
        host: str
    }
    """
    config = None
    try:
        project = request.data["project"]
        relation = request.data["relation"]
        back_async = request.data["async"]
        report = request.data["name"]
        host = request.data["host"]
        config_id = request.data.get("config_id")
    except KeyError:
        return Response(response.KEY_MISS)
    if config_id:
        # 前端有指定config, 会覆盖用例本身的config
        config = literal_eval(models.Config.objects.get(id=config_id).body)

    if host != "请选择":
        host = models.HostIP.objects.get(name=host, project=project).value.splitlines()

    test_sets = []
    suite_list = []
    config_list = []
    for relation_id in relation:
        case_name_id_mapping_list = list(
            models.Case.objects.filter(project__id=project, relation=relation_id)
            .order_by("id")
            .values("id", "name")
        )

        for content in case_name_id_mapping_list:
            test_list = (
                models.CaseStep.objects.filter(case__id=content["id"])
                .order_by("step")
                .values("body")
            )

            testcase_list = []
            for test in test_list:
                body = literal_eval(test["body"])
                if body["request"].get("url"):
                    testcase_list.append(parse_host(ip=host, api=body))
                elif config is None and body["request"].get("base_url"):
                    config = literal_eval(
                        models.Config.objects.get(
                            name=body["name"], project__id=project
                        ).body
                    )
            config_list.append(parse_host(ip=host, api=config))
            test_sets.append(testcase_list)
            config = None
        suite_list.extend(case_name_id_mapping_list)

    if back_async:  # 异步
        tasks.async_debug_suite.delay(
            suite=test_sets,
            project=project,
            obj=suite_list,
            report=report,
            config=config_list,
            user=request.user.id,
        )
        summary = loader.TEST_NOTE_EXISTS
        summary["msg"] = "用例运行中，请稍后查看报告"
    else:
        summary, _ = loader.debug_suite(
            suite=test_sets,
            project=project,
            obj=suite_list,
            config=config_list,
            save=True,
            user=request.user.id,
        )

    return Response(summary)


@api_view(["POST"])
@request_log(level="INFO")
def run_multi_tests(request):
    """
    通过指定id, 运行多个指定用例

    {
        "name": "批量运行2条用例",  # 报告名
        "project": 11,
        "case_config_mapping_list": [
            {
                "config_name": "config_name1,
                "id": 153,  # 用例id
                "name": "case_name1"  # 用例名
            }
        ]
    }
    """
    try:
        project = request.data["project"]
        report_name = request.data["name"]
    except KeyError:
        return Response(response.KEY_MISS)

    # 默认同步运行用例
    back_async = request.data.get("async") or False
    case_config_mapping_list = request.data["case_config_mapping_list"]
    config_body_mapping = {}

    # 解析用例列表中的配置
    for config in case_config_mapping_list:
        config_name = config["config_name"]
        if not config_body_mapping.get(config_name):
            config_body_mapping[config_name] = literal_eval(
                models.Config.objects.get(
                    name=config["config_name"], project__id=project
                ).body
            )
    test_sets = []
    suite_list = []
    config_list = []
    for case_config_mapping in case_config_mapping_list:
        case_id = case_config_mapping["id"]
        config_name = case_config_mapping["config_name"]
        # 获取用例的所有步骤
        case_step_list = (
            models.CaseStep.objects.filter(case__id=case_id)
            .order_by("step")
            .values("body")
        )
        parsed_case_step_list = []
        for case_step in case_step_list:
            body = literal_eval(case_step["body"])
            if body["request"].get("url"):
                parsed_case_step_list.append(body)
        config_body = config_body_mapping[config_name]
        # 记录当前用例的配置信息
        config_list.append(config_body)
        # 记录已经解析好的用例
        test_sets.append(parsed_case_step_list)
    # 用例和配置的映射关系
    suite_list.extend(case_config_mapping_list)

    if back_async:  # 异步
        tasks.async_debug_suite.delay(
            suite=test_sets,
            project=project,
            obj=suite_list,
            report=report_name,
            config=config_list,
            user=request.user.id,
        )
        summary = loader.TEST_NOTE_EXISTS
        summary["msg"] = "用例运行中，请稍后查看报告"
    else:
        summary, _ = loader.debug_suite(
            suite=test_sets,
            project=project,
            obj=suite_list,
            config=config_list,
            save=True,
            user=request.user,
            report_name=report_name,
        )

    return Response(summary)
