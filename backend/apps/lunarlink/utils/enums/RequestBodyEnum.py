# -*- coding: utf-8 -*-
"""
@File    : RequestBodyEnum.py
@Time    : 2023/9/11 16:01
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 请求数据类型
"""
# 请求类型
from enum import IntEnum


class BodyType(IntEnum):
    none = 0
    json = 1
    form = 2
    x_form = 3
    binary = 4
    graphQL = 5
