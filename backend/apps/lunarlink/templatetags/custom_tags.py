# -*- coding: utf-8 -*-
"""
@File    : custom_tags.py
@Time    : 2023/3/8 11:29
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 格式化测试报告中的JSON
"""

import json
import time

from django import template
from loguru import logger

register = template.Library()


@register.filter(name="json_dumps")
def json_dumps(value):
    """将Python对象序列化为JSON格式的字符串
    :param value: 要过滤的变量
    :return:
    """
    try:
        if isinstance(value, dict):
            return json.dumps(
                value, indent=4, separators=(",", ": "), ensure_ascii=False
            )
        else:
            return json.dumps(
                json.loads(value), indent=4, separators=(",", ": "), ensure_ascii=False
            )
    except (TypeError, json.JSONDecodeError) as e:
        logger.error(f"An error occurred while processing JSON: {e}")
        return value


@register.filter(name="convert_timestamp")
def convert_timestamp(value):
    """将时间戳转换为指定格式的本地时间，并返回格式化后的字符串
    :param value: 时间戳
    :return:
    """
    try:
        return time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(int(float(value))))
    except (ValueError, TypeError):
        pass
    return value
