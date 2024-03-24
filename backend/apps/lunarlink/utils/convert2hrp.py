# -*- coding: utf-8 -*-
"""
@File    : convert2hrp.py
@Time    : 2023/2/13 10:29
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

import json
import os
from enum import Enum
from typing import Any, Dict, List, Text, Union, Callable
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from pydantic import HttpUrl

Name = Text
Url = Text
BaseUrl = Union[HttpUrl, Text]
VariablesMapping = Dict[Text, Any]
FunctionsMapping = Dict[Text, Callable]
Headers = Dict[Text, Text]
Cookies = Dict[Text, Text]
Verify = bool
Hooks = List[Union[Text, Dict[Text, Text]]]
Export = List[Text]
Validators = List[Dict]
Env = Dict[Text, Any]


class MethodEnum(Text, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


class TConfig(BaseModel):
    name: Name
    verify: Verify = False
    base_url: BaseUrl = ""
    # Text: prepare variables in debugtalk.py, ${gen_variables(}
    variables: Union[VariablesMapping, Text] = {}
    parameters: Union[VariablesMapping, Text] = {}
    # setup_hooks: Hooks = []
    # teardown_hooks: Hooks = []
    export: Export = []
    path: Text = None
    weight: int = 1


class TRequest(BaseModel):
    """requests.Request model"""

    # TODO: 先注释TRequest-method类型，后期再优化
    method: str
    url: Url
    params: Dict[Text, Text] = {}
    headers: Headers = {}
    req_json: Union[Dict, List, Text] = Field(None)
    body: Union[Text, Dict[Text, Any]] = None
    cookies: Cookies = {}
    timeout: float = 120
    allow_redirects: bool = True
    verify: Verify = False
    upload: Dict = {}  # used for upload files


class TStep(BaseModel):
    name: Name
    request: Union[TRequest, None] = None
    testcase: Union[Text, Callable, None] = None
    variables: VariablesMapping = {}
    setup_hooks: Hooks = []
    # used to extract request's response field
    extract: VariablesMapping = {}
    # used to export session variable from referenced testcase
    export: Export = []
    validators: Validators = Field([], alias="validate")
    validate_script: List[Text] = []


class TestCase(BaseModel):
    config: TConfig
    teststeps: List[TStep]


class Hrp:
    def __init__(self, faster_req_json: Dict):
        self.faster_req_json = faster_req_json

    def parse_url(self):
        url = self.faster_req_json["url"]
        o = urlparse(url=url)
        baseurl = o.scheme + "://" + o.netloc
        return baseurl, o.path

    def get_headers(self):
        headers: Dict = self.faster_req_json.get("headers", {})
        # Content-Length may be error
        headers.pop("Content-Length", None)
        return headers

    def get_request(self) -> TRequest:
        base_url, path = self.parse_url()
        req = TRequest(
            method=self.faster_req_json["method"],
            url=base_url + path,
            params=self.faster_req_json.get("params", {}),
            headers=self.get_headers(),
            body=self.faster_req_json.get("body", {}),
            req_json=self.faster_req_json.get("json", {}),
            verify=self.faster_req_json.get("verify", False),
        )

        return req

    def get_step(self) -> TStep:
        _, path = self.parse_url()
        return TStep(
            name=path,
            request=self.get_request(),
        )

    def get_config(self) -> TConfig:
        base_url, _ = self.parse_url()
        return TConfig(
            name=base_url,
            base_url=base_url,
        )

    def get_testcase(self) -> TestCase:
        config = self.get_config()
        teststeps: List = [self.get_step()]
        return TestCase(
            config=config,
            teststeps=teststeps,
        )
