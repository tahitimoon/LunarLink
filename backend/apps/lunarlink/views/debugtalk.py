# -*- coding: utf-8 -*-
"""
@File    : debugtalk.py
@Time    : 2023/2/22 15:07
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 驱动代码视图
"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lunarlink import models
from lunarlink import serializers
from lunarlink.utils import response
from lunarlink.utils.decorator import request_log
from lunarlink.utils.runner import DebugCode


class DebugTalkView(GenericViewSet):
    """
    DebugTalk update
    """

    serializer_class = serializers.DebugTalkSerializer
    queryset = models.Debugtalk.objects

    @method_decorator(request_log(level="INFO"))
    def debugtalk(self, request, pk):
        """
        获取debugtalk code
        """
        try:
            queryset = models.Debugtalk.objects.get(project__id=pk)
        except ObjectDoesNotExist:
            return Response(response.DEBUGTALK_NOT_EXISTS)

        serializer = self.get_serializer(queryset, many=False)

        return Response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def update(self, request):
        """
        编辑debugtalk.py代码并保存
        {
            id: int # debugtalk id
            code: str
        }
        """

        try:
            debugtalk_id = request.data["id"]
            debugtalk_code = request.data["code"]
        except KeyError:
            return Response(response.KEY_MISS)

        try:
            models.Debugtalk.objects.get(id=debugtalk_id)
            models.Debugtalk.objects.filter(id=debugtalk_id).update(
                code=debugtalk_code,
                updater=request.user.id,
                update_time=timezone.now(),
            )
        except ObjectDoesNotExist:
            return Response(response.DEBUGTALK_NOT_EXISTS)

        return Response(response.DEBUGTALK_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def run(self, request):
        """在线运行"""
        try:
            code = request.data["code"]
        except KeyError:
            return Response(response.KEY_MISS)

        debug = DebugCode(code)
        debug.run()
        resp = {"msg": debug.resp, "success": True, "code": "0001"}
        return Response(resp)
