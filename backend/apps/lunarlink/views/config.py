# -*- coding: utf-8 -*-
"""
@File    : config.py
@Time    : 2023/2/20 14:37
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 配置管理视图
"""
from ast import literal_eval

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from lunarlink import models, serializers
from lunarlink.utils import response
from lunarlink.utils.decorator import request_log
from lunarlink.utils.parser import Format


class ConfigView(GenericViewSet):
    """
    配置管理视图
    """

    serializer_class = serializers.ConfigSerializer
    queryset = models.Config.objects

    @action(detail=False, methods=["get"])
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "project",
                openapi.IN_QUERY,
                description="project id",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="配置名称",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
    )
    @method_decorator(request_log(level="INFO"))
    def list(self, request):
        """
        获取项目管理配置

        query string - project, search
        """
        project = request.query_params.get("project")
        search = request.query_params.get("search")

        queryset = (
            self.get_queryset().filter(project__id=project).order_by("-update_time")
        )

        if search:
            queryset = queryset.filter(name__contains=search)

        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level="DEBUG"))
    def all(self, request, pk):
        """
        获取所有的配置

        """
        queryset = (
            self.get_queryset()
            .filter(project__id=pk)
            .order_by("-update_time")
            .values("id", "name", "is_default", "base_url")
        )

        return Response(queryset)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """
        添加项目配置

        {
            name: str
            project: int
            body: dict
        }
        """

        config = Format(body=request.data, level="config")
        config.parse()

        try:
            config.project = models.Project.objects.get(id=config.project)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        if models.Config.objects.filter(
            name=config.name, project=config.project
        ).first():
            return Response(response.CONFIG_EXISTS)

        config_body = {
            "name": config.name,
            "base_url": config.base_url,
            "body": config.testcase,
            "project": config.project,
        }

        models.Config.objects.create(**config_body, creator=request.user)

        return Response(response.CONFIG_ADD_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def update(self, request, pk):
        """
        更新配置

        {
            name: str,
            base_url: str,
            variables: [],
            parameters: [],
            request: [],
        }
        """
        try:
            config = models.Config.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.CONFIG_NOT_EXISTS)

        format_obj = Format(body=request.data, level="config")
        format_obj.parse()

        if (
            models.Config.objects.exclude(id=pk)
            .filter(name=format_obj.name, project=config.project_id)
            .first()
        ):
            return Response(response.CONFIG_EXISTS)

        case_step = models.CaseStep.objects.filter(
            method="config", name=config.name, case__project_id=config.project_id
        )

        for case in case_step:
            case.name = format_obj.name
            case.body = format_obj.testcase
            case.save()

        config.name = format_obj.name
        config.body = format_obj.testcase
        config.base_url = format_obj.base_url
        if format_obj.is_default is True:
            models.Config.objects.filter(
                project=config.project_id, is_default=True
            ).update(
                is_default=False,
                updater=request.user.id,
                update_time=timezone.now(),
            )
        config.is_default = format_obj.is_default
        config.updater = request.user.id
        config.update_time = timezone.now()
        config.save()

        return Response(response.CONFIG_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def copy(self, request, pk):
        """复制配置
        pk: int
        {
            name: str
        }
        """
        try:
            config = models.Config.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.CONFIG_NOT_EXISTS)

        if models.Config.objects.filter(**request.data, project=config.project).first():
            return Response(response.CONFIG_EXISTS)

        config.id = None
        config.is_default = False
        body = literal_eval(config.body)

        try:
            name = request.data["name"]
        except KeyError:
            return Response(response.KEY_MISS)

        body["name"] = name
        config.name = name
        config.body = body
        config.creator = request.user
        config.updater = request.user.id
        config.save()

        return Response(response.CONFIG_ADD_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def destroy(self, request, pk):
        """
        单个删除

        pk: config id
        """
        try:
            config = models.Config.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.CONFIG_NOT_EXISTS)

        if models.CaseStep.objects.filter(
            method="config",
            name=config.name,
            case__project=config.project,
        ).exists():
            return Response(response.CONFIG_IS_USED)

        config.is_deleted = True
        config.updater = request.user.id
        config.update_time = timezone.now()
        config.save()

        return Response(response.CONFIG_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def bulk_destroy(self, request):
        """
        批量删除配置

        [{id:int}]
        """
        ids = [content["id"] for content in request.data]
        configs = models.Config.objects.filter(id__in=ids)
        if not configs:
            return Response(response.CONFIG_NOT_EXISTS)

        unused_ids = []
        for config in configs:
            if models.CaseStep.objects.filter(
                method="config",
                name=config.name,
                case__project=config.project,
            ).exists():
                continue
            else:
                unused_ids.append(config.id)

        if not unused_ids:
            return Response(response.CONFIG_IS_USED)

        models.Config.objects.filter(id__in=unused_ids).update(
            is_deleted=True,
            update_time=timezone.now(),
            updater=request.user.id,
        )

        return Response(response.CONFIG_DEL_SUCCESS)
