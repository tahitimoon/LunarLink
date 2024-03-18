# -*- coding: utf-8 -*-
"""
@File    : urls.py
@Time    : 2023/1/13 16:09
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 接口路径
"""

from django.urls import path
from lunaruser import views

urlpatterns = [
    path("login", views.LoginView.as_view()),
    path("list", views.UserView.as_view()),
    path(
        "login_log",
        views.LoginLogView.as_view({"get": "list"}),
    ),
]
