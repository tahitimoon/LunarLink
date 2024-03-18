# -*- coding: utf-8 -*-
"""
@File    : record.py
@Time    : 2023/9/7 19:10
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 流量录制->生成case功能
"""
import json
import re

from backend.utils.redis_manager import RedisHelper
from apps.schema.request import RequestInfo


class Recorder:
    def request(self, flow):
        flow.request.headers["X-Forwarded-For"] = flow.client_conn.address[0]

    async def response(self, flow):
        if (
            "47.119.28.171" in flow.request.url
            or flow.request.method.lower() == "options"
            or flow.request.url.endswith(("js", "css", "ttf", "jpg", "svg", "gif"))
        ):
            # 如果是options请求，js等url直接拒绝
            return
        addr = flow.client_conn.address[0]
        record = RedisHelper.get_address_record(addr)
        if not record:
            return
        data = json.loads(record)
        user_id = data.get("user_id", "")
        pattern = re.compile(data.get("regex"))
        if re.findall(pattern, flow.request.url):
            # 说明已开启录制开关，记录状态
            request_data = RequestInfo(flow)
            dump_data = request_data.dumps()
            await RedisHelper.cache_record(user_id=user_id, request=dump_data)
            # TODO: 下个版本需要加入ws协议的支持
