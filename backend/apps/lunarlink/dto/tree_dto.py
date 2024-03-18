# -*- coding: utf-8 -*-
"""
@File    : tree_dto.py
@Time    : 2023/1/14 16:00
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 数据校验
"""

from typing import Dict, List

from pydantic import BaseModel, Field


class TreeUniqueIn(BaseModel):
    project_id: int
    type: int


class TreeUpdateIn(BaseModel):
    tree: List[Dict] = Field(alias="body")
    type: int = Field(alias="type")


class TreeOut(BaseModel):
    tree: List[Dict]
    id: int
    max: int
