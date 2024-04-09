# -*- coding: utf-8 -*-
"""
@File    : tasks.py
@Time    : 2023/2/6 11:07
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 定时任务、异步任务
"""

import logging
from ast import literal_eval
from enum import IntEnum

from celery import shared_task, Task
from django_bulk_update.helper import bulk_update
from django_celery_beat.models import PeriodicTask
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from lunarlink import models
from lunarlink.utils.loader import save_summary, debug_api, debug_suite
from lunarlink.utils.parser import Yapi
from lunarlink.utils import qy_message, email_helper
from lunarlink.utils import response


logger = logging.getLogger(__name__)


class ReportType(IntEnum):
    DEPLOY = 4
    TIMING = 3


def update_task_total_run_count(task_id):
    """增加任务的总运行次数
    :param task_id:
    :return:
    """
    if task_id:
        PeriodicTask.objects.filter(id=task_id).update(
            date_changed=F("date_changed"),
            total_run_count=F("total_run_count") + 1,
        )


class MyBaseTask(Task):
    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        update_task_total_run_count(kwargs.get("task_id"))

    def on_success(self, retval, task_id, args, kwargs):
        update_task_total_run_count(kwargs.get("task_id"))


@shared_task
def async_import_yapi_api(yapi_base_url, yapi_token, project_id):
    """异步导入yapi接口"""
    yapi = Yapi(
        yapi_base_url=yapi_base_url,
        token=yapi_token,
        faster_project_id=project_id,
    )
    apis_imported_from_yapi = models.API.objects.filter(
        project_id=project_id,
        creator__name="yapi",
    )
    imported_apis_mapping = {
        api.yapi_id: api.yapi_up_time for api in apis_imported_from_yapi
    }
    create_ids, update_ids = yapi.get_create_or_update_apis(
        imported_apis_mapping=imported_apis_mapping
    )
    try:
        # 获取yapi的分组, 然后更新api tree
        yapi.create_relation_id(project_id=yapi.faster_project_id)
    except Exception as e:
        logger.error(f"导入yapi失败：{e}")
        return {"status": "error", "message": response.YAPI_ADD_FAILED}

    # 通过id获取所有api的详情
    create_ids.extend(update_ids)
    if not create_ids:
        return {"status": "error", "message": response.YAPI_NOT_NEED_CREATE_OR_UPDATE}

    new_api_instances = []
    update_api_instances = []
    for api_detail in yapi.get_batch_api_detail(api_ids=create_ids):
        # 把yapi解析成符合faster的api格式
        api_instances = yapi.get_parsed_apis(api_info=[api_detail])
        updated_api, new_api = yapi.merge_api(
            api_instances=api_instances,
            apis_imported_from_yapi=apis_imported_from_yapi,
        )
        new_api_instances.extend(new_api)
        update_api_instances.extend(updated_api)

    created_objs = models.API.objects.bulk_create(objs=new_api_instances)
    bulk_update(update_api_instances)

    created_apis_count = len(created_objs)
    updated_apis_count = len(update_api_instances)
    return {
        "status": "success",
        "created_apis_count": created_apis_count,
        "updated_apis_count": updated_apis_count,
    }


@shared_task
def async_debug_api(api, project, name, config=None, user=None):
    """
    异步执行api
    :param api:
    :param project:
    :param name:
    :param config:
    :param user:
    :return:
    """
    summary = debug_api(
        api=api,
        project=project,
        config=config,
        save=False,
        user=user,
    )
    report_id = save_summary(
        name=name,
        summary=summary,
        project=project,
        user=user,
    )

    return {
        "status": "success",
        "report_id": report_id,
    }


@shared_task
def async_debug_suite(suite, project, obj, report, config, user=None):
    """异步执行suite"""
    summary, _ = debug_suite(
        suite=suite,
        project=project,
        obj=obj,
        config=config,
        save=False,
        user=user,
    )
    report_id = save_summary(
        name=report,
        summary=summary,
        project=project,
        user=user,
    )

    return {
        "status": "success",
        "report_id": report_id,
    }


def get_test_suite(args):
    """
    获取测试用例集
    :param args:
    :return:
    """
    case_ids = [pk for pk in args if models.Case.objects.filter(id=pk).exists()]
    cases = models.Case.objects.in_bulk(case_ids)
    return [{"name": case.name, "id": case.id} for case in cases.values()]


def process_override_config(kwargs, project):
    """
    处理覆盖用例原有配置

    :param kwargs:
    :param project:
    :return:
    """
    override_config = kwargs.get("config", "")
    override_config_body = None
    if override_config and override_config != "请选择":
        try:
            override_config_body = literal_eval(
                models.Config.objects.get(
                    name=override_config, project__id=project
                ).body
            )
        except ObjectDoesNotExist:
            logger.error(response.CONFIG_NOT_EXISTS["msg"])
    return override_config_body


def build_test_sets(suite, project, override_config_body):
    """
    构建测试集

    :param suite:
    :param project:
    :param override_config_body:
    :return:
    """
    test_sets = []
    config_list = []
    for content in suite:
        test_list = (
            models.CaseStep.objects.filter(case__id=content["id"])
            .order_by("step")
            .values("body")
        )

        testcase_list = []
        config = None
        for test in test_list:
            body = literal_eval(test["body"])
            if "base_url" in body["request"].keys():
                if override_config_body:
                    config = override_config_body
                    continue
                try:
                    config = literal_eval(
                        models.Config.objects.get(
                            name=body["name"], project__id=project
                        ).body
                    )
                except ObjectDoesNotExist:
                    logger.error(response.CONFIG_NOT_EXISTS["msg"])
                continue
            testcase_list.append(body)
        config_list.append(config)
        test_sets.append(testcase_list)

    return test_sets, config_list


def execute_test_suite(test_sets, project, suite, config_list, is_parallel):
    """
    执行测试套件

    :param test_sets:
    :param project:
    :param suite:
    :param config_list:
    :param is_parallel:
    :return:
    """
    return debug_suite(
        suite=test_sets,
        project=project,
        obj=suite,
        config=config_list,
        allow_parallel=is_parallel,
        save=False,
    )


def prepare_report_details(kwargs):
    """
    准备报告详情

    :param kwargs:
    :return:
    """
    task_name = kwargs["task_name"]
    if kwargs.get("run_type") == "deploy":
        task_name = "部署_" + task_name
        report_type = ReportType.DEPLOY.value
    else:
        report_type = ReportType.TIMING.value

    return task_name, report_type


def save_schedule_summary(task_name, summary, project, report_type):
    """
    保存测试报告

    :param task_name:
    :param summary:
    :param project:
    :param report_type:
    :return:
    """
    return save_summary(
        name=task_name,
        summary=summary,
        project=project,
        report_type=report_type,
    )


def send_notifications(args, kwargs, summary, task_name, report_id):
    """
    发送通知

    :param args:
    :param kwargs:
    :param summary:
    :param task_name:
    :param report_id:
    :return:
    """
    strategy = kwargs.get("strategy")
    if strategy == "始终发送" or (
        strategy == "仅失败发送" and summary["stat"]["failures"] > 0
    ):
        summary.update({"task_name": task_name, "report_id": report_id})
        webhook = kwargs.get("webhook", "")
        email_recipient = kwargs.get("receiver", "")
        email_cc = kwargs.get("mail_cc", "")
        if webhook:
            qy_message.send_message(
                summary=summary,
                webhook=webhook,
                case_count=len(args),
            )
        if email_recipient:
            email_helper.send(
                summary=summary,
                email_recipient=email_recipient,
                email_cc=email_cc,
                case_count=len(args),
            )


@shared_task(base=MyBaseTask, queue="beat_tasks")
def schedule_debug_suite(*args, **kwargs):
    """定时任务"""
    project = kwargs.get("project")
    suite = get_test_suite(args)
    override_config_body = process_override_config(kwargs, project)
    test_sets, config_list = build_test_sets(
        suite=suite,
        project=project,
        override_config_body=override_config_body,
    )

    is_parallel = kwargs.get("is_parallel", False)
    summary, _ = execute_test_suite(
        test_sets=test_sets,
        project=project,
        suite=suite,
        config_list=config_list,
        is_parallel=is_parallel,
    )

    task_name, report_type = prepare_report_details(kwargs)

    report_id = save_schedule_summary(
        task_name=task_name,
        summary=summary,
        project=project,
        report_type=report_type,
    )

    send_notifications(
        args,
        kwargs,
        summary,
        task_name,
        report_id,
    )

    return {
        "status": "success",
        "report_id": report_id,
    }
