# -*- coding: utf-8 -*-
"""
@File    : project.py
@Time    : 2023/1/14 15:54
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 项目视图
"""
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from backend.utils import pagination, permissions
from lunarlink import models
from lunarlink import serializers
from lunarlink.dto.tree_dto import TreeOut, TreeUniqueIn, TreeUpdateIn
from lunarlink.services.tree_service_impl import tree_service
from lunarlink.utils import day, prepare, response
from lunarlink.utils.day import get_day, get_month_format, get_week_format
from lunarlink.utils.decorator import request_log
from lunarlink.utils.response import StandResponse


class ProjectView(GenericViewSet):
    """项目增删查改"""

    serializer_class = serializers.ProjectSerializer
    pagination_class = pagination.MyCursorPagination

    def get_queryset(self):
        # 如果是超级管理员，返回所有项目
        if self.request.user.is_superuser:
            return models.Project.objects.all()

        # 获取当前用户所在的所有分组
        user_groups = self.request.user.groups.all()

        # 返回这些分组相关的项目
        return models.Project.objects.filter(groups__in=user_groups).distinct()

    def get_permissions(self):
        # 如果是 delete 方法，确保用户是管理员
        if self.action == "delete":
            return [permissions.CustomIsAdminUser()]
        return super().get_permissions()

    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        """
        查询项目信息
        """

        projects = self.get_queryset()
        page_projects = self.paginate_queryset(projects)
        serializer = self.get_serializer(page_projects, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """
        添加项目
        """

        try:
            name = request.data["name"]
        except KeyError:
            return Response(response.KEY_MISS)

        if models.Project.objects.filter(name=name).first():
            return Response(response.PROJECT_EXISTS)

        # 反序列化
        serializer = serializers.ProjectSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creator=request.user, updater=request.user.id)
            project = models.Project.objects.get(name=name)
            prepare.project_init(project=project, creator=request.user)
            return Response(response.PROJECT_ADD_SUCCESS)

        return Response(response.SYSTEM_ERROR)

    @method_decorator(request_log(level="INFO"))
    def update(self, request):
        """
        编辑项目
        """
        project_id = request.data.get("id")
        project_name = request.data.get("name")
        try:
            project = models.Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        if project_name != project.name:
            if models.Project.objects.filter(name=project_name).exists():
                return Response(response.PROJECT_EXISTS)

        serializer = self.get_serializer(project, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(response.KEY_MISS)

        # 调用save方法update_time字段才会自动更新
        serializer.save(updater=request.user.id)
        return Response(response.PROJECT_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def delete(self, request):
        """
        删除项目
        """
        try:
            project = models.Project.objects.get(id=request.data["id"])
            project.is_deleted = True
            project.updater = request.user.id
            project.update_time = timezone.now()
            with transaction.atomic():
                project.save()
        except models.Project.DoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)
        except (IntegrityError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(response.PROJECT_DELETE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def single(self, request, pk):
        """
        获取单个项目相关统计信息
        """
        try:
            queryset = models.Project.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        project_info = prepare.get_project_detail_v2(pk=pk)
        # TODO: 屏蔽jira核心用例统计，考虑接入TAPD
        jira_core_case_cover_rate: Dict = prepare.get_jira_core_case_cover_rate(pk=pk)
        project_info.update(jira_core_case_cover_rate)
        project_info.update(serializer.data)

        return Response(project_info)

    @method_decorator(request_log(level="INFO"))
    def yapi_info(self, request, pk):
        """获取项目的yapi地址和token"""
        try:
            obj = models.Project.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)

        ser = self.get_serializer(obj, many=False)
        return Response(ser.data)


class DashBoardView(APIView):
    """项目看板"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        _, report_status = prepare.aggregate_reports_by_status(project_id=0)
        _, report_type = prepare.aggregate_reports_by_type(project_id=0)
        report_day = prepare.aggregate_reports_or_case_bydate(
            date_type="day", model=models.Report
        )
        report_week = prepare.aggregate_reports_or_case_bydate(
            date_type="week", model=models.Report
        )
        report_month = prepare.aggregate_reports_or_case_bydate(
            date_type="month", model=models.Report
        )

        api_day = prepare.aggregate_apis_bydate(date_type="day")
        api_week = prepare.aggregate_apis_bydate(date_type="week")
        api_month = prepare.aggregate_apis_bydate(date_type="month")

        (
            daily_top_api_creators,
            daily_api_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="day",
            model=models.API,
        )
        (
            weekly_top_api_creators,
            weekly_api_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="week",
            model=models.API,
        )
        (
            monthly_top_api_creators,
            monthly_api_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="month",
            model=models.API,
        )

        yapi_day = prepare.aggregate_apis_bydate(date_type="day", is_yapi=True)
        yapi_week = prepare.aggregate_apis_bydate(date_type="week", is_yapi=True)
        yapi_month = prepare.aggregate_apis_bydate(date_type="month", is_yapi=True)

        case_day = prepare.aggregate_reports_or_case_bydate(
            date_type="day", model=models.Case
        )
        case_week = prepare.aggregate_reports_or_case_bydate(
            date_type="week", model=models.Case
        )
        case_month = prepare.aggregate_reports_or_case_bydate(
            date_type="month", model=models.Case
        )

        (
            daily_top_case_creators,
            daily_case_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="day",
            model=models.Case,
        )
        (
            weekly_top_case_creators,
            weekly_case_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="week",
            model=models.Case,
        )
        (
            monthly_top_case_creators,
            monthly_case_creator_counts,
        ) = prepare.aggregate_data_by_date(
            date_type="month",
            model=models.Case,
        )

        res = {
            "report": {
                "status": report_status,
                "type": report_type,
                "week": report_week,
                "month": report_month,
                "day": report_day,
            },
            "case": {
                "week": case_week,
                "month": case_month,
                "day": case_day,
                "daily_top_creators": daily_top_case_creators,
                "daily_creator_counts": daily_case_creator_counts,
                "weekly_top_creators": weekly_top_case_creators,
                "weekly_creator_counts": weekly_case_creator_counts,
                "monthly_top_creators": monthly_top_case_creators,
                "monthly_creator_counts": monthly_case_creator_counts,
            },
            "api": {
                "week": api_week,
                "month": api_month,
                "day": api_day,
                "daily_top_creators": daily_top_api_creators,
                "daily_creator_counts": daily_api_creator_counts,
                "weekly_top_creators": weekly_top_api_creators,
                "weekly_creator_counts": weekly_api_creator_counts,
                "monthly_top_creators": monthly_top_api_creators,
                "monthly_creator_counts": monthly_api_creator_counts,
            },
            "yapi": {"week": yapi_week, "month": yapi_month, "day": yapi_day},
            # 包含今天的前6天
            "recent_days": [get_day(n)[5:] for n in range(-5, 1)],
            "recent_months": [get_month_format(n) for n in range(-5, 1)],
            "recent_weeks": [get_week_format(n) for n in range(-5, 1)],
        }

        return Response(res)


class TreeView(APIView):
    """
    树形结构视图
    """

    @method_decorator(request_log(level="INFO"))
    def get(self, request, pk):
        """
        获取树形结构

        如果没有节点存在，创建一个默认的节点
        """
        tree_type = request.query_params["type"]
        resp: StandResponse[TreeOut] = tree_service.get_or_create(
            TreeUniqueIn(project_id=pk, type=tree_type)
        )
        return Response(resp.dict())

    @method_decorator(request_log(level="INFO"))
    def patch(self, request, pk):
        """
        更新树形结构
        """
        res = tree_service.patch(tree_id=pk, payload=TreeUpdateIn(**request.data))
        return Response(res.dict())


class VisitView(GenericViewSet):
    serializer_class = serializers.VisitSerializer
    queryset = models.Visit.objects

    def list(self, request):
        project = request.query_params.get("project")
        # 查询项目前7天的访问记录
        # 根据日期分组
        # 统计每天的条数
        recent7days = [day.get_day(d)[5:] for d in range(-7, 0)]
        count_data = (
            self.get_queryset()
            .filter(
                project=project, create_time__range=(day.get_day(-7), day.get_day())
            )
            .extra(select={"create_time": "DATE_FORMAT(create_time, '%%m-%%d')"})
            .values("create_time")
            .annotate(counts=Count("id"))
            .values("create_time", "counts")
        )

        create_time_report_map = {
            data["create_time"]: data["counts"] for data in count_data
        }
        report_count = [create_time_report_map.get(d, 0) for d in recent7days]

        return Response({"recent7days": recent7days, "report_count": report_count})
