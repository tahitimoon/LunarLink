# -*- coding: utf-8 -*-
"""
@File    : mycelery.py.py
@Time    : 2023/3/9 16:16
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 设置环境变量，配置Celery应用程序
"""

import logging
import os
from celery import Celery
from celery.signals import after_setup_logger
from django.conf import settings

# 设置Django的环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

# 配置Celery应用程序
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动检测每个已注册应用中的异步任务
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.update(
    CELERY_QUEUES={
        "beat_tasks": {
            "exchange": "beat_tasks",
            "exchange_type": "direct",
            "binding_key": "beat_tasks",
        },
        "work_queue": {
            "exchange": "work_queue",
            "exchange_type": "direct",
            "binding_key": "work_queue",
        },
    },  # 定义任务队列
    CELERY_DEFAULT_QUEUE="work_queue",  # 默认的任务队列
    CELERY_FORCE_EXECV=True,  # 有些情况下可以防止死锁
    task_reject_on_worker_lost=True,  # 任务丢失后拒绝执行
    task_acks_late=True,  # 任务执行完后，不立即删除任务结果
    CELERY_WORKER_CONCURRENCY=2,  # 并发数, 设置得接近于你的CPU核心数，或者稍微高一点
    CELERY_MAX_TASKS_PER_CHILD=50,  # 每个worker最多执行50个任务便自我销毁释放内存
    CELERY_PREFETCH_MULTIPLIER=1,  # 每次从任务队列取任务的数量
    CELERY_ACCEPT_CONTENT=[
        "application/json",  # 指定接受的内容类型
    ],
    CELERY_TASK_SERIALIZER="json",  # 指定任务序列化类型
    CELERY_RESULT_SERIALIZER="json",  # 指定任务结果序列化类型
)


@after_setup_logger.connect
def setup_logger(logger, *args, **kwargs):
    fh = logging.FileHandler("logs/celery.log", "a", encoding="utf-8")
    fh.setLevel(logging.INFO)

    # 再创建一个handler, 用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # 定义handler的输出格式
    formatter = logging.Formatter(
        "%(asctime)s  %(levelname)s  [pid:%(process)d] [%(name)s %(filename)s->%(funcName)s:%(lineno)s] %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
