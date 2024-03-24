# -*- coding: utf-8 -*-
"""
@File    : proxy.py
@Time    : 2023/9/8 17:06
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 启动录制代理
"""
import asyncio
from loguru import logger

from backend import settings
from record_proxy import start_proxy


if __name__ == "__main__":
    if settings.PROXY_ON:
        asyncio.run(start_proxy(logger))
