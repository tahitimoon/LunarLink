# -*- coding: utf-8 -*-
"""
@File    : variables.py
@Time    : 2023/2/22 10:42
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 全局变量视图
"""
from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from lunarlink import models, serializers
from lunarlink.utils import response
from lunarlink.utils.decorator import request_log


class VariablesView(GenericViewSet):
    serializer_class = serializers.VariablesSerializer
    queryset = models.Variables.objects

    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        """查询全局变量"""
        project = request.query_params.get("project")
        search = request.query_params.get("search")

        queryset = (
            self.get_queryset().filter(project__id=project).order_by("-update_time")
        )

        if search:
            queryset = queryset.filter(
                Q(key__contains=search)
                | Q(value__contains=search)
                | Q(description__contains=search)
            )

        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """添加全局变量
        {
            key: str
            value: str
            project: int
        }
        """
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            try:
                project = models.Project.objects.get(id=request.data["project"])
            except ObjectDoesNotExist:
                return Response(response.PROJECT_NOT_EXISTS)

            if models.Variables.objects.filter(
                key=request.data["key"], project=project
            ).filter():
                return Response(response.VARIABLES_EXISTS)

            request.data["project"] = project

            models.Variables.objects.create(
                **request.data,
                creator=request.user,
            )
            return Response(response.VARIABLES_ADD_SUCCESS)
        else:
            res = deepcopy(response.PROJECT_NOT_EXISTS)
            res["msg"] = ser.errors
            return Response(res)

    @method_decorator(request_log(level="INFO"))
    def update(self, request, pk):
        """更新全局变量
        pk: int - 项目id
        {
            id: int - 变量id
            key: str
            value: str
            description: str
        }
        """
        try:
            variable_id = request.data["id"]
            variable_key = request.data["key"]
            variable_value = request.data["value"]
            variable_description = request.data["description"]
        except KeyError:
            return Response(response.KEY_MISS)

        try:
            variables = models.Variables.objects.get(id=variable_id)
        except ObjectDoesNotExist:
            return Response(response.VARIABLES_NOT_EXISTS)

        if (
            models.Variables.objects.exclude(id=variable_id)
            .filter(
                project_id=pk,
                key=variable_key,
            )
            .first()
        ):
            return Response(response.VARIABLES_EXISTS)

        variables.key = variable_key
        variables.value = variable_value
        variables.description = variable_description
        variables.updater = request.user.id
        variables.update_time = timezone.now()
        variables.save()

        return Response(response.VARIABLES_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def destroy(self, request, pk):
        """
        单个删除

        pk: id
        """
        obj = models.Variables.objects.filter(id=pk)
        if not obj:
            return Response(response.VARIABLES_NOT_EXISTS)

        obj.update(
            is_deleted=True,
            update_time=timezone.now(),
            updater=request.user.id,
        )
        return Response(response.VARIABLES_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def bulk_destroy(self, request):
        """批量删除全局变量

        [{id:int}]
        :param request:
        :return:
        """
        ids = [content["id"] for content in request.data]
        objs = models.Variables.objects.filter(id__in=ids)
        if not objs:
            return Response(response.VARIABLES_NOT_EXISTS)
        objs.update(
            is_deleted=True,
            update_time=timezone.now(),
            updater=request.user.id,
        )

        return Response(response.VARIABLES_DEL_SUCCESS)
