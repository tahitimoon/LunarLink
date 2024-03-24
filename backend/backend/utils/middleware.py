# -*- coding: utf-8 -*-
"""
@File    : middleware.py
@Time    : 2023/3/20 15:14
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 记录用户访问网站的行为和数据，并存入数据库
"""
import logging
import time
import traceback

from rest_framework.response import Response
from sentry_sdk import capture_exception

from lunarlink.models import Visit
from lunarlink.utils import qy_message


logger = logging.getLogger(__name__)


class VisitTimesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_request(self, request):
        # 复制一份body的内容，因为原生的body不能被多次访问
        request._body = request.body

    def process_response(self, request, response):
        body = request._body
        if body == b"":
            body = ""
        else:
            body = str(body, encoding="utf-8")

        if request.user is None:
            # 报告页面不需要登录，获取不到用户名
            user = "AnonymousUser"
        else:
            user = request.user

        ip: str = request.META.get(
            "HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")
        )
        # 前端请求头没传project, 就默认为0
        project = request.META.get("HTTP_PROJECT", 0)

        url: str = request.path
        # 去除测试报告页字体相关的访问
        if "/fonts/roboto/" in url:
            return response

        if request.GET != {}:
            query_params = "?"
            # <QueryDict: {'page': ['1'], 'node': [''], 'project': ['11'], 'search': [''], 'tag': ['']}>
            for k, v in request.GET.items():
                query_params += f"{k}={v}&"
            url += query_params[:-1]
        else:
            query_params = ""

        Visit.objects.create(
            user=user,
            url=url,
            request_method=request.method,
            request_body=body,
            ip=ip.split(",")[0],  # 有时候会有多个ip，取第一个
            path=request.path,
            request_params=query_params[1:-1],
            project=project,
        )

        return response


class PerformanceAndExceptionLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        response["X-Page-Duration-ms"] = int(duration * 1000)
        logger.info(
            "duration:%s url:%s parameters:%s",
            duration,
            request.path,
            request.GET.dict(),
        )

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        if exception:
            message_str = f"url: {request.build_absolute_uri()} ** msg: {repr(exception)} ````{traceback.format_exc()}````"
            message_dict = {
                "url": request.build_absolute_uri(),
                "msg": repr(exception),
                "traceback": traceback.format_exc(),
            }

            logger.warning(message_str)

            # send WeChat Work message
            qy_message.send(msg=message_dict)

            # capture exception to sentry:
            capture_exception(exception)

        return Response(
            "Error processing the request, please contact the system administrator.",
            status=500,
        )
