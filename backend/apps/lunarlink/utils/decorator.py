# -*- coding: utf-8 -*-
"""
@File    : decorator.py
@Time    : 2023/1/16 14:43
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 日志
"""

import functools
import logging

from lunarlink.utils import parser

logger = logging.getLogger(__name__)


def request_log(level):
    def wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(request, *args, **kwargs):
            msg_data = (
                f"before process request data:\n{parser.format_json(request.data)}"
            )
            msg_params = f"before process request params:\n{parser.format_json(request.query_params)}"

            if level == "INFO":
                if request.data:
                    logger.info(msg_data)
                if request.query_params:
                    logger.info(msg_params)
            elif level == "DEBUG":
                if request.data:
                    logger.debug(msg_data)
                if request.query_params:
                    logger.debug(msg_params)
            return func(request, *args, **kwargs)

        return inner_wrapper

    return wrapper
