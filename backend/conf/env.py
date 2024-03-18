# -*- coding: utf-8 -*-
"""
@File    : env.py
@Time    : 2023/6/29 15:53
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""
# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = "root"
# 数据库密码
DATABASE_PASSWORD = ""
# 数据库名
DATABASE_NAME = "lunarlink"

# ================================================= #
# ************** RabbitMQ配置 ************** #
# ================================================= #
MQ_USER = "guest"
MQ_PASSWORD = ""
MQ_HOST = "127.0.0.1"
MQ_URL = f"amqp://{MQ_USER}:{MQ_PASSWORD}@{MQ_HOST}:5672//"

# ================================================= #
# ************** Redis配置 ************** #
# ================================================= #
REDIS_ON = True
REDIS_HOST = "127.0.0.1"
REDIS_PASSWORD = ""
REDIS_PORT = 6379
REDIS_DB = 0

# ================================================= #
# ************** 其他 配置  ************** #
# ================================================= #
DEBUG = True  # 线上环境请设置为False

# 启动登录日志记录(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True
ALLOWED_HOSTS = ["*"]
BASE_REPORT_URL = "http://localhost:8000/api/lunarlink/reports"

IM_REPORT_SETTING = {
    "base_url": "http://localhost",
    "port": 8000,
    "report_title": "自动化测试报告",
}


# ================================================= #
# ************** 监控告警企微机器人配置  ************** #
# ================================================= #
QY_WEB_HOOK = ""  # 测试环境不需要机器人通知

# ================================================= #
# ************** 发送邮件配置  ************** #
# ================================================= #
# 使用 SMTP 服务器发送邮件
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# SMTP 服务器地址
EMAIL_HOST = "smtphz.qiye.163.com"

# SMTP 服务器端口
EMAIL_PORT = 465

# 发件人邮箱账号
EMAIL_HOST_USER = ""
DEFAULT_FROM_EMAIL = ""

# 发件人邮箱密码
EMAIL_HOST_PASSWORD = ""

# 是否使用 TLS
EMAIL_USE_TLS = False

# 是否使用 SSL
EMAIL_USE_SSL = True

# ================================================= #
# ************** 录制流量代理配置  ************** #
# ================================================= #
# PROXY Server
PROXY_ON = True  # 是否开启代理
PROXY_PORT = 7778
