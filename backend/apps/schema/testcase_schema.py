# -*- coding: utf-8 -*-
"""
@File    : testcase_schema.py
@Time    : 2023/9/11 16:05
@Author  : geekbing
@LastEditTime : 2023/10/09 16:05
@LastEditors : geekbing
@Description : API、Case数据模板
"""
from typing import Dict, List

from pydantic import BaseModel, Field


class HeadersData(BaseModel):
    header: Dict = {}
    desc: Dict = {}


class RequestFormSchema(BaseModel):
    data: Dict = {}
    desc: Dict = {}


class RequestParamsSchema(BaseModel):
    params: Dict = {}
    desc: Dict = {}


class FilesSchema(BaseModel):
    files: Dict = {}
    desc: Dict = {}


class RequestData(BaseModel):
    form: RequestFormSchema = RequestFormSchema()
    params: RequestParamsSchema = RequestParamsSchema()
    files: FilesSchema = FilesSchema()
    json_data: Dict = Field({}, alias="json")


class VariablesData(BaseModel):
    variables: List = []
    desc: Dict = {}


class HooksData(BaseModel):
    setup_hooks: List = []
    teardown_hooks: List = []


class ValidateData(BaseModel):
    check: List[Dict] = Field(
        [{"equals": ["status_code", 200, "默认断言"]}], alias="validate"
    )


class ExtractData(BaseModel):
    extract: List = []
    desc: Dict = {}


class APIBodySchema(BaseModel):
    header: HeadersData = HeadersData()
    request: RequestData = RequestData()
    extract: ExtractData = ExtractData()
    check: ValidateData = Field(ValidateData(), alias="validate")
    variables: VariablesData = VariablesData()
    hooks: HooksData = HooksData()
    name: str = ""
    url: str = ""
    method: str = ""
    times: int = 1


class RecordCaseSchema(BaseModel):
    length: int
    project_id: int
    relation: int
    name: str
    tag: int
    body: List
