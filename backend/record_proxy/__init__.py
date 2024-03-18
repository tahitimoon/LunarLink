# -*- coding: utf-8 -*-
"""
@File    : __init__.py.py
@Time    : 2023/9/7 19:09
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""
from backend import settings

from record_proxy.record import Recorder


async def start_proxy(log):
    """
    启动代理
    :param log: 日志
    :return:
    """
    try:
        from mitmproxy import options
        from mitmproxy.tools.dump import DumpMaster
    except ImportError:
        log.bind(name=None).warning(
            "mitmproxy未安装，请参见: https://docs.mitmproxy.org/stable/overview-installation/"
        )
        return

    addons = [Recorder()]
    try:
        opts = options.Options(listen_host="0.0.0.0", listen_port=settings.PROXY_PORT)
        m = DumpMaster(opts, with_termlog=False, with_dumper=False)
        block_addon = m.addons.get("block")
        m.addons.remove(block_addon)
        m.addons.add(*addons)
        log.bind(name=None).debug(
            f"proxy server is running at http://0.0.0.0:{settings.PROXY_PORT}"
        )
        await m.run()
    except Exception as e:
        log.bind(name=None).error(
            f"proxy server running failed, if all nodes run failed, please check: {e}"
        )
