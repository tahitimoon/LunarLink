# -*- coding: utf-8 -*-
"""
@File    : request_util.py
@Time    : 2024/1/15 10:15
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : Request工具类
"""
import logging

from typing import Dict

import requests
from django.conf import settings
from user_agents import parse

from lunarlink.models import LoginLog

logger = logging.getLogger(__name__)


def get_request_ip(request):
    """
    获取请求IP
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        # X-Forwarded-For 可能有一个代理链，因此这里取第一个即客户端的真实 IP
        ip = x_forwarded_for.split(",")[0].strip()
        return ip
    ip = request.META.get("REMOTE_ADDR", "") or getattr(request, "request_ip", None)
    return ip or "unknown"


def get_ip_analysis(ip) -> Dict:
    """
    获取IP解析数据
    :param ip: ip地址
    :return:
    """
    data = {
        "continent": "",
        "country": "",
        "province": "",
        "city": "",
        "district": "",
        "isp": "",
        "area_code": "",
        "country_english": "",
        "country_code": "",
        "longitude": "",
        "latitude": "",
    }
    if ip != "unknown" and ip:
        if getattr(settings, "ENABLE_LOGIN_ANALYSIS_LOG", True):
            # url = f"https://ip-api.com/json/{ip}?lang=zh-CN"
            try:
                res = requests.get(
                    url="https://ip.django-vue-admin.com/ip/analysis",
                    params={"ip": ip},
                    timeout=5,
                )
                if res.status_code == 200:
                    res_data = res.json()
                    if res_data.get("code") == 0:
                        data = res_data.get("data")
            except Exception as e:
                logger.error(e)
    return data


def get_browser(request):
    """
    获取浏览器
    :param request:
    :return:
    """
    ua_string = request.META["HTTP_USER_AGENT"]
    user_agent = parse(ua_string)
    return user_agent.get_browser()


def get_os(request):
    """
    获取操作系统
    :param request:
    :return:
    """
    ua_string = request.META["HTTP_USER_AGENT"]
    user_agent = parse(ua_string)
    return user_agent.get_os()


def save_login_log(request):
    """
    保存登录日志
    :param request: 请求对象
    :return:
    """
    ip = get_request_ip(request=request)

    # 过滤掉平台自身的服务器 IP 地址
    platform_ips = ["127.0.0.1", "47.119.28.171"]
    # 如果请求来自平台自身的 IP，跳过记录日志
    if ip in platform_ips:
        return

    analysis_data = get_ip_analysis(ip=ip)
    analysis_data.update(
        {
            "ip": ip,
            "username": request.user.username,
            "name": request.user.name,
            "agent": str(parse(request.META.get("HTTP_USER_AGENT", ""))),
            "browser": get_browser(request=request),
            "os": get_os(request=request),
            "creator_id": request.user.id,
        }
    )
    LoginLog.objects.create(**analysis_data)
