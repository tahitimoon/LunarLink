# -*- coding: utf-8 -*-
"""
@File    : error.py
@Time    : 2023/10/9 15:42
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""


class BaseError(Exception):
    pass


class RedisError(BaseError):
    """redis error"""

    pass


class NotFoundError(BaseError):
    pass


class TaskTimeIllegal(BaseError):
    pass


class TaskNotFound(BaseError):
    pass


class RelationNotFound(BaseError):
    pass


class FunctionNotFound(NotFoundError):
    pass


class VariableNotFound(NotFoundError):
    pass


class ApiNotFound(NotFoundError):
    pass


class CaseStepNotFound(NotFoundError):
    pass


class ConfigNotFound(NotFoundError):
    pass


class TestCaseNotFound(NotFoundError):
    pass


class TaskNotFound(NotFoundError):
    pass
