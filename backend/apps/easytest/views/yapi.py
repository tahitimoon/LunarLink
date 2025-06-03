# -*- coding: utf-8 -*-
"""
@File    : yapi.py
@Time    : 2023/2/15 17:51
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : Yapi视图
"""

import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response

from lunarlink import tasks
from lunarlink.utils import response
from lunarlink import models


logger = logging.getLogger(__name__)


class YAPIView(APIView):
    def post(self, request, pk):
        try:
            obj = models.Project.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(response.PROJECT_NOT_EXISTS)
        yapi_token = obj.yapi_openapi_token
        yapi_base_url = obj.yapi_base_url
        task = tasks.async_import_yapi_api.delay(
            yapi_base_url,
            yapi_token,
            pk,
        )

        response.IMPORT_YAPI.update({"task_id": task.id})
        return Response(response.IMPORT_YAPI)
