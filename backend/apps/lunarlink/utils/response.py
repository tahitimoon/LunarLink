# -*- coding: utf-8 -*-
"""
@File    : response.py
@Time    : 2023/1/14 16:37
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 响应错误码
"""
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


class ErrorMsg(BaseModel):
    code: str = "0001"
    msg: str = "成功"
    success: bool = True


GenericResultsType = TypeVar("GenericResultsType")


class StandResponse(ErrorMsg, GenericModel, Generic[GenericResultsType]):
    data: GenericResultsType


RECORD_START_SUCCESS = {
    "code": "0001",
    "success": True,
    "msg": "开始录制，可以在浏览器/app上操作啦！",
}

RECORD_IS_RUNNING = {"code": "0005", "success": False, "msg": "此IP正在录制中"}

RECORD_STOP_SUCCESS = {
    "code": "0002",
    "success": True,
    "msg": "停止成功，快去生成用例吧~",
}

RECORD_REMOVE_SUCCESS = {"code": "0003", "success": True, "msg": "删除成功"}

RECORD_DATA_ERROR = {"code": "0101", "success": False, "msg": "无http请求，请检查参数"}

API_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "接口添加成功"}

API_GET_SUCCESS = {"code": "0012", "success": True, "msg": "获取数据成功"}

API_NOT_FOUND = {"code": "0102", "success": False, "msg": "未查询到该接口"}

API_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "接口修改成功"}

API_DEL_SUCCESS = {"code": "0003", "success": True, "msg": "接口删除成功"}

CASE_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "用例添加成功"}

CASE_GENERATOR_SUCCESS = {
    "code": "0001",
    "success": True,
    "msg": "用例生成成功, 快去列表查看吧~",
}

CASE_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "用例修改成功"}

TAG_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "用例标记成功"}

CASE_EXISTS = {
    "code": "0101",
    "success": False,
    "msg": "此节点下已存在该用例, 请重新命名",
}

CASE_NOT_EXISTS = {"code": "0102", "success": False, "msg": "此用例不存在"}

CASE_IS_USED = {
    "code": "0104",
    "success": False,
    "msg": "用例被定时任务使用中, 无法删除",
}

CASE_SPILT_SUCCESS = {"code": "0001", "success": True, "msg": "用例切割成功"}

CASE_DELETE_SUCCESS = {"code": "0003", "success": True, "msg": "用例删除成功"}

CONFIG_EXISTS = {"code": "0101", "success": False, "msg": "此配置名已存在, 请重新命名"}

CONFIG_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "配置添加成功"}

CONFIG_NOT_EXISTS = {"code": "0102", "success": False, "msg": "指定的配置不存在"}

CONFIG_MISSING = {"code": "0103", "success": False, "msg": "缺少配置文件"}

CONFIG_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "配置修改成功"}

CONFIG_DEL_SUCCESS = {"code": "0003", "success": True, "msg": "配置删除成功"}

CONFIG_IS_USED = {
    "code": "0104",
    "success": False,
    "msg": "配置文件被用例使用中, 无法删除",
}

DEBUGTALK_NOT_EXISTS = {"code": "0102", "success": False, "msg": "debugtalk不存在"}

DEBUGTALK_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "debugtalk更新成功"}

DATA_TO_LONG = {"code": "0100", "success": False, "msg": "数据信息过长"}


REPORT_DEL_SUCCESS = {"code": "0003", "success": True, "msg": "报告删除成功"}

REPORT_NOT_EXISTS = {"code": "0102", "success": False, "msg": "指定的报告不存在"}

TREE_GET_SUCCESS = {"code": "0001", "success": True, "msg": "目录获取成功"}

TREE_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "目录更新成功"}

TREE_NOT_EXISTS = {"code": "0102", "success": False, "msg": "目录不存在"}

PROJECT_EXISTS = {"code": "0101", "success": False, "msg": "项目名称已存在, 请重新命名"}

PROJECT_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "项目添加成功"}

SYSTEM_ERROR = {"code": "9999", "success": False, "msg": "System Error"}

KEY_MISS = {"code": "0100", "success": False, "msg": "请求数据非法"}

PROJECT_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "项目修改成功"}

PROJECT_DELETE_SUCCESS = {"code": "0003", "success": True, "msg": "项目删除成功"}

PROJECT_NOT_EXISTS = {"code": "0102", "success": False, "msg": "项目不存在"}

CASE_STEP_SYNC_SUCCESS = {"code": "0002", "success": True, "msg": "用例步骤同步成功"}

CASE_STEP_NOT_EXIST = {"code": "0102", "success": False, "msg": "指定的用例步骤不存在"}

TASK_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "任务新增成功"}

TASK_ADD_FAILURE = {"code": "0101", "success": False, "msg": "任务新增失败"}

TASK_COPY_FAILURE = {
    "code": "0103",
    "success": False,
    "msg": "任务复制失败, 任务名已存在",
}

TASK_COPY_SUCCESS = {"code": "0003", "success": True, "msg": "任务复制成功"}

TASK_DEL_SUCCESS = {"code": "0003", "success": True, "msg": "任务删除成功"}

TASK_RUN_SUCCESS = {
    "code": "0001",
    "success": True,
    "msg": "用例运行中, 请稍后查看报告",
}

TASK_TIME_ILLEGAL = {"code": "0101", "success": False, "msg": "时间表达式非法"}

TASK_HAS_EXISTS = {
    "code": "0102",
    "success": False,
    "msg": "无法添加, 该任务名称已被使用",
}

TASK_NOT_EXISTS = {"code": "0102", "success": False, "msg": "指定的任务不存在"}

TASK_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "任务修改成功"}

TASK_UPDATE_FAILURE = {"code": "0102", "success": False, "msg": "任务修改失败"}

TASK_DUPLICATE_NAME = {"code": "0104", "success": False, "msg": "相同任务名已存在"}

TASK_CI_PROJECT_IDS_EXIST = {
    "code": "0103",
    "success": False,
    "msg": "Gitlab项目id已存在其他项目",
}

VARIABLES_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "全局变量添加成功"}

VARIABLES_DEL_SUCCESS = {"code": "0003", "success": True, "msg": "全局变量删除成功"}

VARIABLES_UPDATE_SUCCESS = {"code": "0002", "success": True, "msg": "全局变量修改成功"}

VARIABLES_EXISTS = {"code": "0101", "success": False, "msg": "此变量已存在, 请重新命名"}

VARIABLES_NOT_EXISTS = {"code": "0102", "success": False, "msg": "指定的全局变量不存在"}

YAPI_ADD_SUCCESS = {"code": "0001", "success": True, "msg": "导入YAPI接口添加成功"}

IMPORT_YAPI = {
    "code": "0001",
    "success": True,
    "msg": "如果是首次导入，可能时间稍长，请耐心等待~",
}

YAPI_ADD_FAILED = {"code": "0103", "success": False, "msg": "导入YAPI接口失败"}

YAPI_NOT_NEED_CREATE_OR_UPDATE = {
    "code": "0002",
    "success": True,
    "msg": "没有需要新增和更新的接口",
}

PERMISSION_DENIED = {"code": "0403", "success": False, "msg": "权限不足"}
