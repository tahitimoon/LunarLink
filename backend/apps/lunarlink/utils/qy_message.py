# -*- coding: utf-8 -*-
"""
@File    : qy_message.py
@Time    : 2023/3/13 14:04
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 企微机器人发送消息
"""
import logging
import json

from typing import Dict, Union

import requests
from django.conf import settings

from lunarlink.utils.message_template import parse_message, qy_msg_template

logger = logging.getLogger(__name__)


def send_message(summary: Union[Dict, str], webhook: str, **kwargs):
    """
    发送企业微信消息

    :param summary:
    :param webhook:
    :param kwargs:
    :return:
    """
    header = {"Content-Type": "application/json"}
    webhooks = webhook.split("\n")  # 多个机器人，换行分隔
    for webhook in webhooks:
        parsed_data = parse_message(summary=summary, **kwargs)
        message = qy_msg_template(**parsed_data)
        res = requests.post(
            url=webhook, headers=header, data=json.dumps(message).encode("utf-8")
        ).json()
        if res.get("errcode") == 0:
            logger.info(f"发送通知成功，请求的webhook是: {webhook}")
        else:
            logger.error(f"发送通知失败，请求的webhook是: {webhook}， 响应是：{res}")


def send(msg: Dict, mentioned_list=None, mentioned_mobile_list=None):
    """ """
    if mentioned_mobile_list is None:
        mentioned_mobile_list = []
    if mentioned_list is None:
        mentioned_list = []
    webhook = settings.QY_WEB_HOOK

    header = {"Content-Type": "application/json"}
    content = f"""<font color=\'info\'>**LunarLink平台预警**</font> \n
    >url: <font color=\'comment\'>{msg.get("url")}</font>
    >msg: <font color=\'comment\'>{msg.get("msg")}</font>
    >traceback: <font color=\'warning\'>{msg.get("traceback")}</font>"""
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
            "mentioned_list": mentioned_list,
            "mentioned_mobile_list": mentioned_mobile_list,
        },
    }
    res = requests.post(url=webhook, headers=header, json=data).json()
    if res.get("errcode") == 0:
        logger.info(f"发送通知成功，请求的webhook是: {webhook}")
    else:
        logger.error(f"发送通知失败，请求的webhook是: {webhook}， 响应是：{res}")
