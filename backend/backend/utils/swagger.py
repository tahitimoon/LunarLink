# -*- coding: utf-8 -*-
"""
@File    : swagger.py
@Time    : 2023/1/13 18:22
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

from drf_yasg.inspectors import SwaggerAutoSchema


class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        tags = super().get_tags(operation_keys)

        if "api" in tags and len(operation_keys) >= 3:
            # `operation_keys` 内容像这样 ['v1', 'prize_join_log', 'create']
            if operation_keys[2].startswith('run'):
                tags[0] = 'run'
            else:
                tags[0] = operation_keys[2]

        return tags
