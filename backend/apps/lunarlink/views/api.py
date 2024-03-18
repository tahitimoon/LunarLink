# -*- coding: utf-8 -*-
"""
@File    : api.py
@Time    : 2023/2/1 16:57
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : API视图
"""
from enum import IntEnum
from typing import List

from ast import literal_eval

from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from apps.exceptions.error import RelationNotFound
from lunarlink import models, serializers
from lunarlink.utils import response
from lunarlink.utils.decorator import request_log
from lunarlink.utils.query_filters import filter_by_time_range, filter_by_node
from lunarlink.utils.parser import Format, Parse
from lunarlink.utils.enums.TreeTypeEnum import TreeType


class APITag(IntEnum):
    DEPRECATED = 4  # 已废弃


class APITemplateView(GenericViewSet):
    """
    API操作视图
    """

    serializer_class = serializers.APISerializer
    queryset = models.API.objects.filter(~Q(tag=APITag.DEPRECATED.value))

    @swagger_auto_schema(query_serializer=serializers.AssertSerializer())
    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        """
        api-获取api列表

        支持多种条件搜索
        """

        ser = serializers.AssertSerializer(data=request.query_params)
        if ser.is_valid():
            node = ser.validated_data.get("node")
            project = ser.validated_data.get("project")
            search: str = ser.validated_data.get("search")
            tag = ser.validated_data.get("tag")
            rig_env = ser.validated_data.get("rigEnv")
            showYAPI = ser.validated_data.get("showYAPI")
            creator = ser.validated_data.get("creator")
            start_time = ser.validated_data.get("start_time")
            end_time = ser.validated_data.get("end_time")

            queryset = (
                self.get_queryset().filter(project=project).order_by("-create_time")
            )
            # 根据创建时间过滤
            queryset = filter_by_time_range(queryset, start_time, end_time)

            if creator:
                queryset = queryset.filter(creator__name=creator)

            if showYAPI is False:
                queryset = queryset.filter(~Q(creator__name="yapi"))

            if search != "":
                search: List = search.split()
                for key in search:
                    queryset = queryset.filter(
                        Q(name__contains=key) | Q(url__contains=key)
                    )
            try:
                queryset = filter_by_node(queryset, project, node, TreeType.API.value)
            except RelationNotFound:
                return Response(response.TREE_NOT_EXISTS)

            if tag != "":
                queryset = queryset.filter(tag=tag)

            if rig_env != "":
                queryset = queryset.filter(rig_env=rig_env)

            pagination_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pagination_queryset, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            response_data = {
                **response.API_GET_SUCCESS,
                "data": paginated_response.data,
            }
            return Response(response_data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """
        api-新增一个api

        前端按照格式组装好，注意body
        """

        api = Format(request.data)
        api.parse()

        api_body = {
            "name": api.name,
            "body": api.testcase,
            "url": api.url,
            "method": api.method,
            "project": models.Project.objects.get(id=api.project),
            "relation": api.relation,
            "creator": request.user,
        }

        try:
            models.API.objects.create(**api_body)
        except DataError:
            return Response(response.DATA_TO_LONG)

        return Response(response.API_ADD_SUCCESS)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "header": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "header": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Header 对象"
                        ),
                        "desc": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Header 描述"
                        ),
                    },
                ),
                "request": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "form": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "data": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Form data 对象"
                                ),
                                "desc": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Form data 描述"
                                ),
                            },
                        ),
                        "json": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="JSON 对象"
                        ),
                        "params": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "params": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Params 对象"
                                ),
                                "desc": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Params 描述"
                                ),
                            },
                        ),
                        "files": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "files": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Files 对象"
                                ),
                                "desc": openapi.Schema(
                                    type=openapi.TYPE_OBJECT, description="Files 描述"
                                ),
                            },
                        ),
                    },
                ),
                "extract": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "extract": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                            description="Extract 数组",
                        ),
                        "desc": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Extract 描述"
                        ),
                    },
                ),
                "validate": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "validate": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                            description="Validate 数组",
                        ),
                    },
                ),
                "variables": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "variables": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                            description="Variables 数组",
                        ),
                        "desc": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Variables 描述"
                        ),
                    },
                ),
                "hooks": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "setup_hooks": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Setup hooks 数组",
                        ),
                        "teardown_hooks": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Teardown hooks 数组",
                        ),
                    },
                ),
                "url": openapi.Schema(type=openapi.TYPE_STRING, description="URL"),
                "method": openapi.Schema(type=openapi.TYPE_STRING, description="请求方法"),
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="名称"),
                "times": openapi.Schema(type=openapi.TYPE_INTEGER, description="次数"),
                # 添加其他自定义字段
            },
        )
    )
    @method_decorator(request_log(level="INFO"))
    def update(self, request, pk):
        """
        api-更新单个api

        更新单个api的内容
        """
        api = Format(request.data)
        api.parse()

        api_body = {
            "name": api.name,
            "body": api.testcase,
            "url": api.url,
            "method": api.method,
            "updater": request.user.id,
            "update_time": timezone.now(),
        }

        objs = models.API.objects.filter(id=pk)
        if objs:
            objs.update(**api_body)
        else:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def move(self, request):
        """
        api-批量更新api的目录

        移动api到指定目录
        """
        project: int = request.data.get("project")
        relation: int = request.data.get("relation")
        apis: List = request.data.get("api")
        ids = [api["id"] for api in apis]

        objs = models.API.objects.filter(project=project, id__in=ids)
        if objs:
            objs.update(
                relation=relation,
                updater=request.user.id,
                update_time=timezone.now(),
            )
        else:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def copy(self, request, pk):
        """
        api-复制api

        复制一个api
        """
        name = request.data.get("name")
        try:
            api = models.API.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)
        body = literal_eval(api.body)
        body["name"] = name
        api.body = body
        api.id = None
        api.name = name
        api.creator = request.user
        api.updater = request.user.id
        api.save()
        return Response(response.API_ADD_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def destroy(self, request, pk):
        """
        api-删除单个api

        pk: api id
        """
        obj = models.API.objects.filter(id=pk)
        if not obj:
            return Response(response.API_NOT_FOUND)

        obj.update(
            is_deleted=True,
            updater=request.user.id,
            update_time=timezone.now(),
        )
        return Response(response.API_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def bulk_destroy(self, request):
        """
        批量删除api

        [{id:int}]
        """
        ids = [content["id"] for content in request.data]
        objs = models.API.objects.filter(Q(id__in=ids) & Q(is_deleted=False))
        if not objs:
            return Response(response.API_NOT_FOUND)
        objs.update(
            is_deleted=True,
            update_time=timezone.now(),
            updater=request.user.id,
        )

        return Response(response.API_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def add_tag(self, request):
        """
        api-更新api的tag, 暂时默认为调式成功, 接口文档参数与实际传参不一致需优化

        更新api的tag类型
        """
        api_ids: List = request.data.get("api_ids", [])

        if api_ids:
            updated_rows = models.API.objects.filter(pk__in=api_ids).update(
                tag=request.data.get("tag"),
                update_time=timezone.now(),
                updater=request.user.id,
            )
            if updated_rows > 0:
                return Response(response.API_UPDATE_SUCCESS)

        return Response(response.API_NOT_FOUND)

    @method_decorator(request_log(level="INFO"))
    def sync_case(self, request, pk):
        """
        api-同步api到case_step

        1.根据api_id查出("name", "body", "url", "method")
        2.根据api_id更新case_step中的("name", "body", "url", "method", "updater")
        3.更新case的update_time, updater
        """
        source_api = (
            models.API.objects.filter(pk=pk)
            .values("name", "body", "url", "method", "project")
            .first()
        )
        # 根据api反向查出project
        project = source_api.pop("project")

        project_case_ids = models.Case.objects.filter(project=project).values_list(
            "id", flat=True
        )
        # 限制case_step只在当前项目
        case_steps = models.CaseStep.objects.filter(
            source_api_id=pk, case_id__in=project_case_ids
        )

        case_steps.update(
            **source_api,
            updater=request.user.id,
            update_time=timezone.now(),
        )
        case_ids = case_steps.values_list("case", flat=True)
        # 限制case只在当前项目
        models.Case.objects.filter(pk__in=list(case_ids), project=project).update(
            update_time=timezone.now(),
            updater=request.user.id,
        )
        return Response(response.CASE_STEP_SYNC_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def single(self, request, pk):
        """
        api-获取单个api详情，返回body信息

        获取单个api的详细情况
        """
        try:
            api = models.API.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        parse = Parse(literal_eval(api.body))
        parse.parse_http()

        resp = {
            "id": api.id,
            "body": parse.testcase,
            "success": True,
            "creator": api.creator.name,
            "relation": api.relation,
            "project": api.project.id,
        }

        return Response(resp)
