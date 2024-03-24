# -*- coding: utf-8 -*-
"""
@File    : docker.py
@Time    : 2023/6/29 15:53
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : docker部署配置
"""
import os

# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# 数据库地址
DATABASE_HOST = os.getenv("DATABASE_HOST")
# 数据库端口
DATABASE_PORT = os.getenv("DATABASE_PORT", 3306)
# 数据库用户名
DATABASE_USER = os.getenv("DATABASE_USER")
# 数据库密码
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
# 数据库名
DATABASE_NAME = os.getenv("DATABASE_NAME")

# ================================================= #
# ************** RabbitMQ配置 ************** #
# ================================================= #
MQ_USER = os.getenv("MQ_USER")
MQ_PASSWORD = os.getenv("MQ_PASSWORD")
MQ_HOST = os.getenv("MQ_HOST")
MQ_PORT = os.getenv("MQ_PORT")
MQ_URL = f"amqp://{MQ_USER}:{MQ_PASSWORD}@{MQ_HOST}:{MQ_PORT}//"

# ================================================= #
# ************** Redis配置 ************** #
# ================================================= #
REDIS_ON = os.getenv("REDIS_ON", "True") == "True"
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

# ================================================= #
# ************** 其他 配置  ************** #
# ================================================= #
DEBUG = False  # 线上环境请设置为False

# 启动登录日志记录(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True

ALLOWED_HOSTS = ["*"]

BASE_REPORT_URL = os.getenv("BASE_REPORT_URL")  # 替换成部署的服务器地址

IM_REPORT_SETTING = {
    "base_url": os.getenv("IM_REPORT_BASE_URL"),
    "port": os.getenv("IM_REPORT_PORT", 8081),
    "report_title": os.getenv("IM_REPORT_TITLE"),
}

# ================================================= #
# ************** 监控告警企微机器人配置  ************** #
# ================================================= #
QY_WEB_HOOK = os.getenv("QY_WEB_HOOK")  # 企微机器人webhook地址

# ================================================= #
# ************** 发送邮件配置  ************** #
# ================================================= #
# 使用 SMTP 服务器发送邮件
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")

# SMTP 服务器地址
EMAIL_HOST = os.getenv("EMAIL_HOST")

# SMTP 服务器端口
EMAIL_PORT = os.getenv("EMAIL_PORT")

# 发件人邮箱账号
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
# 发件人邮箱密码
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# 是否使用 TLS
EMAIL_USE_TLS = False
# 是否使用 SSL
EMAIL_USE_SSL = True

# ================================================= #
# ************** 录制流量代理配置  ************** #
# ================================================= #
# PROXY Server
PROXY_ON = os.getenv("PROXY_ON", "True") == "True"  # 是否开启代理
PROXY_PORT = int(os.getenv("PROXY_PORT"))
