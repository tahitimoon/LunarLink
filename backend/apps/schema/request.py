# -*- coding: utf-8 -*-
"""
@File    : request.py
@Time    : 2023/9/8 15:06
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 转化mitmproxy请求和响应数据（request and response data）
"""
import json
from typing import TypeVar

import pydantic
from loguru import logger


body = TypeVar("body", bytes, str)


class RequestInfo(pydantic.BaseModel):
    url: str
    body: str
    request_method: str
    request_headers: dict
    response_headers: dict
    cookies: dict
    request_cookies: dict
    response_content: str
    status_code: int

    def __init__(self, flow=None, **kwargs):
        if flow:
            kwargs.update(
                dict(
                    status_code=flow.response.status_code,
                    url=flow.request.url,
                    request_method=flow.request.method,
                    request_headers=dict(flow.request.headers),
                    response_headers=dict(flow.response.headers),
                    response_content=self.get_response(flow.response),
                    body=self.get_body(flow.request),
                    cookies=dict(flow.response.cookies),
                    request_cookies=dict(flow.request.cookies),
                )
            )
        super().__init__(**kwargs)

    @classmethod
    def translate_json(cls, request_data):
        """
        将请求数据转换为json格式

        :param request_data: 接口请求数据
        :return: 返回json格式字符串
        """
        try:
            if isinstance(request_data, dict):
                return json.dumps(request_data, indent=4, ensure_ascii=False)
            else:
                return json.dumps(
                    json.loads(request_data), indent=4, ensure_ascii=False
                )
        except (TypeError, json.JSONDecodeError) as e:
            logger.bind(name=None).warning(f"解析json格式失败: {e}")
            return request_data

    @classmethod
    def get_response(cls, response):
        content_type = response.headers.get("Content-Type").lower()
        if "json" in content_type:
            return cls.translate_json(response.text)
        if "text" in content_type or "xml" in content_type:
            return response.text
        return response.data.decode("utf-8")

    @classmethod
    def get_body(cls, request):
        if len(request.content) == 0:
            return ""
        content_type = request.headers.get("Content-Type").lower()
        if "json" in content_type:
            return cls.translate_json(request.text)
        if "text" in content_type or "xml" in content_type:
            return request.text
        if "x-www-form-urlencoded" in content_type:
            return json.dumps(dict(request.urlencoded_form))
        return request.data.decode("utf-8")

    def dumps(self):
        return json.dumps(self.dict(), ensure_ascii=False)
