# -*- coding: utf-8 -*-
"""
@File    : har_convertor.py
@Time    : 2023/9/11 15:48
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : request转化器，支持har
"""
from typing import List
from apps.schema.request import RequestInfo


class Convertor:
    @staticmethod
    def convert(file, regex: str = None) -> List[RequestInfo]:
        raise NotImplementedError
