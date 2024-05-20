# -*- coding: utf-8 -*-
"""
@File    : task.py
@Time    : 2023/3/9 10:57
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

import json
import logging

from django_celery_beat import models as celery_models

from apps.exceptions.error import TaskNotFound
from lunarlink.utils.parser import format_json


logger = logging.getLogger(__name__)


class Task:
    """
    定时任务操作
    """

    def __init__(self, **body):
        """
        数据初始化
        :param body: 请求体数据
        """
        logger.info(f"before process task data:\n {format_json(body)}")
        self.__name = body["name"]
        self.__data = body["data"]
        self.__crontab = body["crontab"]
        self.__switch = body["switch"]
        self.__task = "lunarlink.tasks.schedule_debug_suite"
        self.__project = body["project"]
        self.__email = {
            "strategy": body["strategy"],
            "mail_cc": body.get("mail_cc"),
            "receiver": body.get("receiver"),
            "crontab": self.__crontab,
            "project": self.__project,
            "task_name": self.__name,
            "webhook": body.get("webhook"),
            "updater": body.get("updater"),
            "creator": body.get("creator"),
            "ci_project_ids": body.get("ci_project_ids", []),
            "ci_env": body.get("ci_env", "请选择"),
            "is_parallel": body.get("is_parallel", False),
            "config": body.get("config", "请选择"),
        }
        self.__crontab_time = None

    def format_crontab(self):
        """
        格式化时间
        """
        cron_fields = self.__crontab.split(" ")
        self.__crontab_time = {
            "day_of_week": cron_fields[4],
            "month_of_year": cron_fields[3],
            "day_of_month": cron_fields[2],
            "hour": cron_fields[1],
            "minute": cron_fields[0],
        }

    def add_task(self):
        """
        add tasks
        """
        self.format_crontab()

        crontab = celery_models.CrontabSchedule.objects.filter(
            **self.__crontab_time
        ).first()
        if crontab is None:
            crontab = celery_models.CrontabSchedule.objects.create(
                **self.__crontab_time
            )
        celery_models.PeriodicTask.objects.create(
            name=f"{self.__project}_{self.__name}",  # 兼容定时任务名称必须唯一
            task=self.__task,
            args=json.dumps(self.__data, ensure_ascii=False),
            kwargs=json.dumps(self.__email, ensure_ascii=False),
            enabled=self.__switch,
            description=self.__project,
            crontab=crontab,
        )

    def update_task(self, task_id):
        """
        update task

        :param task_id:
        :return:
        """
        self.format_crontab()
        task_obj = celery_models.PeriodicTask.objects.filter(id=task_id)
        if not task_obj:
            raise TaskNotFound

        crontab = celery_models.CrontabSchedule.objects.filter(
            **self.__crontab_time
        ).first()
        if crontab is None:
            crontab = celery_models.CrontabSchedule.objects.create(
                **self.__crontab_time
            )
        task_obj.save(
            name=f"{self.__project}_{self.__name}",
            crontab=crontab,
            enabled=self.__switch,
            args=json.dumps(self.__data, ensure_ascii=False),
            kwargs=json.dumps(self.__email, ensure_ascii=False),
        )
