# -*- coding: utf-8 -*-
"""
@File    : pagination.py
@Time    : 2023/1/13 16:06
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 分页查询
"""

from rest_framework import pagination


class MyCursorPagination(pagination.CursorPagination):
    """
    Cursor 光标分页 性能高 安全
    """

    page_size = 10
    ordering = "-create_time"
    page_size_query_param = "pages"
    max_page_size = 40


class MyPageNumberPagination(pagination.PageNumberPagination):
    """
    普通分页，数据量越大性能越差
    """

    page_size = 10
    page_size_query_param = "size"
    page_query_param = "page"
    max_page_size = 40
