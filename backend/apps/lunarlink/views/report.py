# -*- coding: utf-8 -*-
"""
@File    : report.py
@Time    : 2023/2/13 09:42
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 测试报告视图
"""
import json
import re
from ast import literal_eval
from shlex import quote
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.utils import pagination
from lunarlink import models, serializers
from lunarlink.utils import response
from lunarlink.utils.convert2hrp import Hrp
from lunarlink.utils.decorator import request_log


class ConvertRequest:
    @classmethod
    def _to_curl(cls, request, compressed: bool = False, verify: bool = True):
        """Return string with curl command by provided request object

        :param request:
        :param compressed: If `True` then `--compressed` argument will be added to result
        :param verify:
        :return:
        """

        parts = [
            ("curl", None),
            ("-X", request.method),
        ]
        parts += [
            (None, request.url),
        ]

        for k, v in sorted(request.headers.items()):
            parts += [("-H", "{0}: {1}".format(k, v))]

        if request.body:
            body = request.body
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            if isinstance(body, dict):
                body = json.dumps(body)
            parts += [("-d", body)]

        if compressed:
            parts += [("--compressed", None)]

        if not verify:
            parts += [("--insecure", None)]

        flat_parts = []
        for k, v in parts:
            if k:
                flat_parts.append(quote(k))
            if v:
                flat_parts.append(quote(v))

                if k == "-H":
                    flat_parts.append(" \\\n")

        return " ".join(flat_parts)

    @classmethod
    def _make_fake_req(cls, request_meta_dict):
        class RequestMeta:
            ...

        req = RequestMeta()
        setattr(req, "method", request_meta_dict["method"])
        setattr(req, "url", request_meta_dict["url"])
        setattr(req, "headers", request_meta_dict["headers"])
        body = request_meta_dict.get("body") or request_meta_dict.get("data")
        setattr(req, "body", body)
        return req

    @classmethod
    def to_curl(cls, req: Dict) -> str:
        _req = cls._make_fake_req(req)
        return cls._to_curl(_req, compressed=True, verify=False)

    @classmethod
    def to_hrp(cls, req: Dict) -> Dict:
        hrp = Hrp(faster_req_json=req)
        return hrp.get_testcase().dict()

    @classmethod
    def generate_curl(cls, report_details, convert_type=("curl",)):
        for detail in report_details:
            for record in detail["records"]:
                meta_data = record["meta_data"]
                for t in convert_type:
                    req = meta_data["request"]
                    method_name = f"to_{t}"
                    method = getattr(ConvertRequest, method_name)
                    record["meta_data"][t] = method(req)


class ReportView(GenericViewSet):
    """报告视图"""

    queryset = models.Report.objects
    serializer_class = serializers.ReportSerializer
    pagination_class = pagination.MyPageNumberPagination

    def get_authenticators(self):
        # 查看报告详情不需要鉴权
        pattern = re.compile(r"/api/lunarlink/reports/\d+")
        if (
            self.request.method == "GET"
            and re.search(pattern, self.request.path) is not None
        ):
            return []  # 不需要任何鉴权
        return super().get_authenticators()  # 默认所有鉴权

    def get_permissions(self):
        # 如果是look方法，不需要任何权限
        if self.action == "look":
            return [AllowAny()]
        return super().get_permissions()

    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        """获取测试报告列表"""

        project = request.query_params.get("project")
        search = request.query_params.get("search")
        report_type = request.query_params.get("reportType")
        report_status = request.query_params.get("reportStatus")
        only_me = request.query_params.get("onlyMe")

        queryset = (
            self.get_queryset().filter(project__id=project).order_by("-update_time")
        )

        # 前端传过来是小写的字符串，不是python的True
        if only_me == "true":
            queryset = queryset.filter(creator=request.user)

        if search != "":
            queryset = queryset.filter(name__contains=search)

        if report_type != "":
            queryset = queryset.filter(type=report_type)

        if report_status != "":
            queryset = queryset.filter(status=report_status)

        page_report = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page_report, many=True)
        return self.get_paginated_response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def look(self, request, pk):
        """
        查看报告

        查看报告详情
        """
        try:
            report = models.Report.objects.get(id=pk)
            report_detail = models.ReportDetail.objects.get(report__id=pk)
        except ObjectDoesNotExist:
            return Response(response.REPORT_NOT_EXISTS)

        summary = json.loads(report.summary)
        summary["details"] = literal_eval(report_detail.summary_detail)
        ConvertRequest.generate_curl(summary["details"], convert_type=("curl",))
        summary["html_report_name"] = report.name

        return render(request, template_name="report_template.html", context=summary)

    @method_decorator(request_log(level="INFO"))
    def destroy(self, request, pk):
        """
        单个删除

        pk: id
        """
        report_obj = models.Report.objects.filter(id=pk).first()
        if not report_obj:
            return Response(response.REPORT_NOT_EXISTS)
        report_obj.is_deleted = True
        report_obj.updater = request.user.id
        report_obj.update_time = timezone.now()
        report_obj.save()  # 这将触发 pre_save 信号，并执行 delete_related_report_detail 处理器函数

        return Response(response.REPORT_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def bulk_destroy(self, request):
        """
        批量删除报告

        [{id:int}]
        """
        ids = [content["id"] for content in request.data]
        # TODO: 如果有大量的数据，考虑性能问题
        objs = list(models.Report.objects.filter(id__in=ids))  # 将QuerySet转换为list
        if not objs:
            return Response(response.REPORT_NOT_EXISTS)

        try:
            with transaction.atomic():
                models.Report.objects.filter(id__in=ids).update(
                    is_deleted=True,
                    update_time=timezone.now(),
                    updater=request.user.id,
                )
                models.ReportDetail.objects.filter(report__in=objs).update(
                    is_deleted=True
                )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response(response.REPORT_DEL_SUCCESS)

    # TODO: 下载报告 待实现
    @method_decorator(request_log(level="INFO"))
    def download(self, request, **kwargs):
        """下载报告"""
        pass
