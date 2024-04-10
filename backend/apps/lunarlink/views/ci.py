# -*- coding: utf-8 -*-
"""
@File    : CI.py
@Time    : 2023/3/14 11:25
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 持续集成CI视图
"""

import datetime
import json
import re
import time

from ast import literal_eval
from typing import Dict

import xmltodict
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django_celery_beat.models import PeriodicTask
from drf_yasg.utils import swagger_auto_schema

from lunarlink import models
from lunarlink.utils import loader, qy_message
from lunarlink.utils.decorator import request_log
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from lunarlink.serializers import CISerializer, CIReportSerializer
from lunarlink.utils.loader import save_summary
from lunarlink.utils import response


def summary2junit(summary: Dict) -> Dict:
    """初始化JUnit的数据结构
    :param summary:
    :return:
    """
    res = {
        "testsuites": {
            "testsuite": {
                "errors": 0,
                "failures": 0,
                "hostname": "",
                "name": "",
                "skipped": 0,
                "tests": 0,
                "time": "0",
                "timestamp": "20210524T18:04:50.941913",
                "testcase": [],
            }
        }
    }

    time_info = summary.get("time")
    res["testsuites"]["testsuite"]["time"] = time_info.get("duration")
    start_at: str = time_info.get("start_at")
    timestamp = datetime.datetime.fromtimestamp(int(float(start_at))).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )
    res["testsuites"]["testsuite"]["timestamp"] = timestamp

    details = summary.get("details", [])
    res["testsuites"]["testsuite"]["tests"] = len(details)
    for detail in details:
        test_case = build_testcase(detail, res)
        res["testsuites"]["testsuite"]["testcase"].append(test_case)

    return res


def build_testcase(detail, res):
    """
    构建Junit Testcase
    :param detail:
    :param res:
    :return:
    """
    test_case = {"classname": "", "file": "", "line": "", "name": "", "time": ""}
    name = detail.get("name")
    test_case["classname"] = name  # 对应junit的Suite
    records = detail.get("records")
    test_case["line"] = len(records)
    test_case["time"] = detail["time"]["duration"]
    result = detail.get("success")
    step_names = []
    for index, record in enumerate(records):
        step_names.append(f"{index}-{record['name']}")
    test_case["name"] = "\n".join(step_names)  # 对应junit的每个case的Name

    # 记录错误case的详细信息
    if result is False:
        case_error, failure_details = build_failure_detail(records)
        if case_error:
            res["testsuites"]["testsuite"]["errors"] += 1
        else:
            res["testsuites"]["testsuite"]["failures"] += 1

        failure = {"message": "断言或者抽取失败", "#text": "\n".join(failure_details)}
        test_case["failure"] = failure

    return test_case


def build_failure_detail(records):
    """记录错误case的详细信息
    :param records:
    :return:
    """
    case_error = False
    failure_details = []
    for index, record in enumerate(records):
        step_status = record.get("status")
        if step_status == "failure":
            failure_details.append(
                f"{index}-{record['name']}\n{record.get('attachment')}\n{'*' * 68}"
            )
        elif step_status == "error":
            case_error = True
    return case_error, failure_details


class CIView(GenericViewSet):
    authentication_classes = []
    serializer_class = CISerializer
    pagination_class = None

    @swagger_auto_schema(operation_summary="gitlab-ci触发自动化用例运行")
    @method_decorator(request_log(level="INFO"))
    def run_ci_tests(self, request):
        """
        gitlab-ci发送请求

        测试平台解析参数，定时任务中的ci_project_ic和ci_env同时匹配时，返回触发执行任务
        """
        ser = CISerializer(data=request.data)
        if ser.is_valid():
            task_name = "lunarlink.tasks.schedule_debug_suite"
            ci_project_id: int = ser.validated_data.get("ci_project_id")
            ci_env: str = ser.validated_data.get("env")

            query = PeriodicTask.objects.filter(enabled=1, task=task_name)
            pk_kwargs_list = query.values("pk", "kwargs", "description")
            enabled_task_ids = []
            project = None
            for pk_kwargs in pk_kwargs_list:
                pk: int = pk_kwargs["pk"]
                kwargs: dict = json.loads(pk_kwargs["kwargs"])
                ci_project_ids: list = literal_eval(
                    kwargs.get("ci_project_ids") or "[]"
                )
                if isinstance(ci_project_ids, int):
                    ci_project_ids = [ci_project_ids]

                # 定时任务中的ci_project_id和ci_env同时匹配
                if (
                    ci_project_id in ci_project_ids
                    and ci_env
                    and ci_env == kwargs.get("ci_env")
                ):
                    enabled_task_ids.append(pk)
                    project = pk_kwargs["description"]

            # 没有匹配用例，直接返回
            if not enabled_task_ids:
                timestamp = datetime.datetime.fromtimestamp(int(time.time())).strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                )
                not_found_case_res = {
                    "testsuites": {
                        "testsuite": {
                            "errors": 0,
                            "failures": 0,
                            "hostname": "",
                            "name": "没有找到匹配的用例",
                            "skipped": 0,
                            "tests": 0,
                            "time": "0",
                            "timestamp": timestamp,
                            "testcase": [],
                        }
                    }
                }

                xml_data = xmltodict.unparse(not_found_case_res)
                return HttpResponse(xml_data, content_type="text/xml")

            test_sets = []
            suite_list = []
            config_list = []
            config = None
            webhook_set = set()
            override_config_body = None
            for task_id in enabled_task_ids:
                task_obj = query.filter(id=task_id).first()
                # 如果task中存在重载配置，就覆盖用例中的配置
                override_config = json.loads(task_obj.kwargs).get("config")
                if (
                    override_config_body is None
                    and override_config
                    and override_config != "请选择"
                ):
                    try:
                        override_config_body = literal_eval(
                            models.Config.objects.get(
                                name=override_config, project__id=project
                            ).body
                        )
                    except ObjectDoesNotExist:
                        return Response(response.CONFIG_NOT_EXISTS)

                if task_obj:
                    # 判断webhook是否合法
                    case_ids = task_obj.args
                    url = json.loads(task_obj.kwargs).get("webhook")
                    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
                    if re.match(url_pattern, url):
                        webhook_set.add(url)
                else:
                    continue
                # 反查出一个task中包含的所有用例
                suite = list(
                    models.Case.objects.filter(pk__in=literal_eval(case_ids))
                    .order_by("id")
                    .values("id", "name")
                )
                for case in suite:
                    case_step_list = (
                        models.CaseStep.objects.filter(case__id=case["id"])
                        .order_by("step")
                        .values("body")
                    )
                    testcase_list = []
                    for case_step in case_step_list:
                        body = literal_eval(case_step["body"])
                        if body["request"].get("url"):
                            testcase_list.append(body)
                        elif config is None and body["request"].get("base_url"):
                            # 当前步骤时配置
                            # 如果task中存在重载配置，就覆盖用例中的配置
                            if override_config_body:
                                config = override_config_body
                            else:
                                try:
                                    config = literal_eval(
                                        models.Config.objects.get(
                                            name=body["name"], project__id=project
                                        ).body
                                    )
                                except ObjectDoesNotExist:
                                    return Response(response.CONFIG_NOT_EXISTS)
                    config_list.append(config)
                    test_sets.append(testcase_list)
                    config = None
                suite_list.extend(suite)
                override_config_body = None
            # 同步运行用例
            summary, _ = loader.debug_suite(
                suite=test_sets,
                project=project,
                obj=suite_list,
                config=config_list,
                save=False,
            )
            ci_project_namespace = ser.validated_data["ci_project_namespace"]
            ci_project_name = ser.validated_data["ci_project_name"]
            ci_job_id = ser.validated_data["ci_job_id"]
            summary["name"] = f"{ci_project_namespace}_{ci_project_name}_job{ci_job_id}"

            report_id = save_summary(
                name=summary.get("name"),
                summary=summary,
                project=project,
                report_type=4,
                user=ser.validated_data["start_job_user"],
                ci_metadata=ser.validated_data,
            )
            junit_results = summary2junit(summary)
            xml_data = xmltodict.unparse(junit_results)
            summary["task_name"] = "gitlab-ci_" + summary.get("name")
            summary["report_id"] = report_id
            for webhook in webhook_set:
                # TODO: 还需要优化企微发送，加入ci集成参数
                qy_message.send_message(
                    summary=summary,
                    webhook=webhook,
                    ci_job_url=ser.validated_data["ci_job_url"],
                    ci_pipeline_url=ser.validated_data["ci_pipeline_url"],
                    case_count=junit_results["testsuites"]["testsuite"]["tests"],
                )
            return HttpResponse(xml_data, content_type="text/xml")
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        query_serializer=CIReportSerializer(),
        operation_summary="获取gitlab-ci运行的报告url",
    )
    def get_ci_report_url(self, request):
        """获取gitlab-ci运行的报告url"""
        ser = CIReportSerializer(data=request.query_params)
        if ser.is_valid():
            ci_job_id = ser.validated_data["ci_job_id"]
            report_obj = models.Report.objects.filter(ci_job_id=ci_job_id).first()
            if report_obj:
                report_url = f"{settings.BASE_REPORT_URL}/{report_obj.id}/"
            else:
                return Response(data=f"查找的ci_job_id: {ci_job_id}不存在")
            return Response(data=report_url)
        else:
            return Response(data=ser.errors, status=status.HTTP_400_BAD_REQUEST)
