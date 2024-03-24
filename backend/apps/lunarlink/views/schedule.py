# -*- coding: utf-8 -*-
"""
@File    : schedule.py
@Time    : 2023/3/9 10:42
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 定时任务视图
"""
import logging
import json
from ast import literal_eval

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_celery_beat import models
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from apps.exceptions.error import TaskNotFound
from backend.utils import pagination
from backend.celery import app
from lunarlink import serializers
from lunarlink.utils import response
from lunarlink.utils.decorator import request_log
from lunarlink.utils.task import Task


logger = logging.getLogger(__name__)


class ScheduleView(GenericViewSet):
    """
    定时任务增删改查
    """

    queryset = models.PeriodicTask.objects
    serializer_class = serializers.PeriodicTaskSerializer
    pagination_class = pagination.MyPageNumberPagination

    @method_decorator(request_log(level="INFO"))
    def list(self, request):
        """
        获取定时任务列表

        query string
        """
        project = request.query_params.get("project")
        task_name = request.query_params.get("task_name")
        creator = request.query_params.get("creator")
        schedule = (
            self.get_queryset().filter(description=project).order_by("-date_changed")
        )

        if task_name:
            schedule = schedule.filter(name__contains=task_name)
        if creator:
            schedule = schedule.filter(kwargs__contains=f'"creator": "{creator}"')

        page_schedule = self.paginate_queryset(schedule)
        serializer = self.get_serializer(page_schedule, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """
        新增定时任务

        {
            name: str
            crontab: str
            switch: bool
            data: [int, int]
            strategy: str
            receiver: str
            copy: str
            project: int
        }
        """
        project = request.data.get("project")
        name = request.data.get("name")
        if models.PeriodicTask.objects.filter(
            name=f"{project}_{name}", description=project
        ).exists():
            return Response(response.TASK_HAS_EXISTS)

        ser = serializers.ScheduleDeSerializer(data=request.data)
        if ser.is_valid():
            request.data.update({"creator": request.user.name})
            task = Task(**request.data)
            try:
                task.add_task()
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}", exc_info=True)
                return Response({"error": "An unexpected error occurred"}, status=500)
            return Response(response.TASK_ADD_SUCCESS)
        else:
            return Response({**response.TASK_ADD_FAILURE, "msg": ser.errors})

    @method_decorator(request_log(level="INFO"))
    def update(self, request, pk):
        """
        更新定时任务

        """
        project = request.data.get("project")
        name = request.data.get("name")
        if models.PeriodicTask.objects.filter(
            ~Q(id=pk), name=f"{project}_{name}"
        ).exists():
            return Response(response.TASK_DUPLICATE_NAME)

        ser = serializers.ScheduleDeSerializer(data=request.data)
        if ser.is_valid():
            task = Task(**request.data)
            try:
                task.update_task(task_id=pk)
            except TaskNotFound:
                return Response(response.TASK_NOT_EXISTS)
            return Response(response.TASK_UPDATE_SUCCESS)
        else:
            return Response({**response.TASK_UPDATE_FAILURE, "msg": ser.errors})

    @method_decorator(request_log(level="INFO"))
    def patch(self, request, pk):
        """
        更新任务的状态

        {"switch": bool}
        """
        try:
            switch = request.data["switch"]
        except KeyError:
            return Response(response.KEY_MISS)

        try:
            task_obj = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response(response.TASK_NOT_EXISTS)

        task_obj.enabled = switch
        kwargs = json.loads(task_obj.kwargs)
        kwargs["updater"] = request.user.name
        task_obj.kwargs = json.dumps(kwargs, ensure_ascii=False)
        task_obj.save()
        return Response(response.TASK_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def delete(self, request, pk):
        """
        删除任务

        query string
        """
        try:
            task = models.PeriodicTask.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.TASK_NOT_EXISTS)

        task.enabled = False  # 关闭任务
        task.delete()
        return Response(response.TASK_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def copy(self, request, pk):
        """
        复制定时任务

        {"name": string}
        """
        try:
            task_name = request.data["name"]
        except KeyError:
            return Response(response.KEY_MISS)

        try:
            task_obj = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response(response.TASK_NOT_EXISTS)

        if task_obj.name == task_name:
            return Response(response.TASK_COPY_FAILURE)

        if (
            self.get_queryset()
            .filter(name=f"{task_obj.description}_{task_name}")
            .exists()
        ):
            return Response(response.TASK_COPY_FAILURE)

        task_obj.id = None
        task_obj.name = f"{task_obj.description}_{task_name}"
        task_obj.total_run_count = 0
        kwargs = json.loads(task_obj.kwargs)
        kwargs["creator"] = request.user.name
        kwargs["updater"] = ""
        task_obj.kwargs = json.dumps(kwargs, ensure_ascii=False)
        task_obj.save()
        return Response(response.TASK_COPY_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def run(self, request, pk):
        """
        手动执行定时任务

        query string
        """
        try:
            task_obj = models.PeriodicTask.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.TASK_NOT_EXISTS)

        task_name = "lunarlink.tasks.schedule_debug_suite"
        args = literal_eval(task_obj.args)
        kwargs = json.loads(task_obj.kwargs)
        kwargs["task_id"] = task_obj.id
        app.send_task(
            name=task_name,
            args=args,
            kwargs=kwargs,
            queue="beat_tasks",
        )
        return Response(response.TASK_RUN_SUCCESS)
