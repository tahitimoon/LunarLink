# -*- coding: utf-8 -*-
"""
@File    : email_helper.py
@Time    : 2023/9/8 11:05
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 邮件发送
"""
import logging
from typing import Dict, Union

from django.core.mail import EmailMessage

from lunarlink.utils.message_template import parse_message, email_msg_template

logger = logging.getLogger(__name__)


def send_mail_with_cc(
    subject: str,
    html_message: str,
    recipient_list: list[str],
    cc_list: list[str] = None,
) -> bool:
    """
    发送带有抄送人的HTML邮件

    :param subject: 邮件主题
    :param html_message: HTML格式的邮件内容
    :param recipient_list: 收件人邮箱列表
    :param cc_list: 抄送人邮箱列表
    :return: 发送邮件成功返回True，失败返回False
    """
    email = EmailMessage(
        subject=subject,
        body=html_message,
        to=recipient_list,
        cc=cc_list,
    )
    email.content_subtype = "html"
    return email.send()


def send(summary: Union[Dict, str], email_recipient: str, email_cc: str, **kwargs):
    """
    发送邮件

    :param summary: 报告摘要
    :param email_recipient: 邮件接收人
    :param email_cc: 邮件抄送人
    :param kwargs:
    :return:
    """
    recipient_list = email_recipient.split(";")
    ccr_list = email_cc.split(";")
    parsed_data = parse_message(summary=summary, **kwargs)
    message = email_msg_template(**parsed_data)
    is_send = send_mail_with_cc(
        recipient_list=recipient_list,
        cc_list=ccr_list,
        **message,
    )
    if is_send:
        logger.info(f"邮件发送成功, 收件人：{email_recipient}，抄送人：{email_cc}")
    else:
        logger.error(f"邮件发送失败, 收件人：{email_recipient}，抄送人：{email_cc}")
