# -*- coding: utf-8 -*-
"""
@File    : generator.py
@Time    : 2023/9/11 15:47
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 根据RequestInfo生成测试用例
"""
import logging
import json
import re
from collections import defaultdict
from enum import IntEnum
from typing import Any, Dict, List, Tuple, Union, Set

from urllib.parse import urlparse, parse_qs

from apps.exceptions.convert import GenerateError
from apps.schema.request import RequestInfo
from apps.schema.api_schema import APIBody, APISchema
from apps.schema.testcase_schema import RecordCaseSchema, APIBodySchema
from lunarlink.models import API
from lunarlink.utils.enums.RequestBodyEnum import BodyType
from lunarlink.utils.parser import Format


logger = logging.getLogger(__name__)


class CaseTag(IntEnum):
    INTEGRATION_CASE = 2


# 忽略的字段
ignored_headers = {
    "content-type",
    "connection",
    "date",
    "content-length",
    "host",
    "access-control-allow-credentials",
    "access-control-allow-origin",
    "user-agent",
    "server",
}


class CaseGenerator:
    """
    根据RequestInfo数组生成测试用例
    """

    @staticmethod
    def ignore(key: str):
        """
        检查指定的HTTP头部字段名称是否在预定义的忽略列表中。

        :param key: 忽略字段 headers.Origin
        :return: 如果字段应被忽略，则返回True；否则返回False。
        """
        for ig in ignored_headers:
            if key.lower().endswith(ig):
                return True
        return False

    @staticmethod
    def get_body_type(headers: Dict):
        headers = {k.lower(): v for k, v in headers.items()}
        content_type = headers.get("content-type", "").lower()
        if "json" in content_type:
            return BodyType.json
        if "x-www-form" in content_type:
            return BodyType.x_form
        if "form" in content_type:
            return BodyType.form
        return BodyType.none

    @staticmethod
    def extract_variables(input_string: str):
        """
        使用正则表达式提取 ${http_res_INDEX_variable::path} 格式的变量、索引和路径

        :param input_string:
        :return: 返回http_res_INDEX, http_res_INDEX_variable, path
        """
        matches = re.findall(r"\$http_res_(\d+)_(.*?)::(.+)", input_string)
        if matches:
            idx, var_name, path = matches[0]
            full_variable = "http_res_" + idx + "_" + var_name
            return "http_res_" + idx, full_variable, path
        return None

    @staticmethod
    def generate_case(
        length: int,
        project_id: int,
        case_dir: int,
        api_dir: int,
        config: Dict,
        case_name: str,
        requests: List[RequestInfo],
        user: int,
    ) -> Tuple[RecordCaseSchema, List]:
        """
        根据录制接口生成测试用例

        :param api_dir: 接口目录
        :param length:
        :param project_id:
        :param case_dir: 用例目录
        :param config:
        :param case_name:
        :param requests:
        :param user: 当前用户
        :return:
        """
        record_case_body = [config]
        api_info_map = {}

        # 先将requests转成faster格式api
        for r in range(len(requests)):
            api_info = APIBodySchema()  # 初始化 faster 格式的 api 模板
            api_name = f"http_res_{r + 1}"
            api_info.name = api_name
            api_info.method = requests[r].request_method
            # 请求头
            headers = requests[r].request_headers
            CaseGenerator.merge_headers(headers, api_info)
            # 请求参数为: form、json
            requests_body = requests[r].body
            if requests_body:
                CaseGenerator.merge_body(headers, api_info, requests_body)
            # 请求参数为: params
            CaseGenerator.merge_params(api_info, requests[r].url)

            api_info_map.update({api_name: api_info.dict(by_alias=True)})  # 保持别名

        # 遍历所有接口，将htt_res_1_token的值content.token加入extract
        for api_name, request_data in api_info_map.items():
            for headers_key, headers_value in request_data["header"]["header"].items():
                CaseGenerator.append_extract(
                    request_data, api_info_map, headers_key, headers_value, "headers"
                )

            for k, v in request_data["request"]["form"]["data"].items():
                CaseGenerator.append_extract(request_data, api_info_map, k, v, "form")

            for k, v in request_data["request"]["json"].items():
                CaseGenerator.append_extract(request_data, api_info_map, k, v, "form")

            for k, v in request_data["request"]["params"]["params"].items():
                CaseGenerator.append_extract(request_data, api_info_map, k, v, "params")

        api_instances = []
        for _, v in api_info_map.items():
            api = Format(v)
            api.parse()
            if api_dir:
                api_body = APIBody(**api.testcase)
                api_schema = APISchema(
                    name=api.name,
                    body=api_body,
                    url=api.url,
                    method=api.method,
                    project_id=project_id,
                    relation=api_dir,
                    creator_id=user,
                ).dict(by_alias=True)
                api_instances.append(API(**api_schema))
            record_case_body.append({"body": api.testcase})

        return (
            RecordCaseSchema(
                length=length,
                project_id=project_id,
                relation=case_dir,
                name=case_name,
                tag=CaseTag.INTEGRATION_CASE.value,
                body=record_case_body,
            ),
            api_instances,
        )

    @staticmethod
    def merge_headers(headers: Dict, api_info: APIBodySchema):
        """
        将录制接口中的headers格式化后加入fastapi的headers中

        :param headers: 录制接口中的headers
        :param api_info: fastapi接口数据
        :return:
        """
        api_info.header.header.update(headers)
        api_info.header.desc.update({key: "" for key in headers.keys()})

    @staticmethod
    def merge_body(headers: Dict, api_info: APIBodySchema, body: str):
        """
        将录制接口中的body格式化后加入fastapi的body中

        :param headers: 录制接口中的headers
        :param api_info: fastapi接口数据
        :param body: 接口请求body
        :return:
        """
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"转换body变量失败: {e}")
        else:
            body_type = CaseGenerator.get_body_type(headers)
            if body_type == BodyType.x_form:
                api_info.request.form.data.update(body)
                api_info.request.form.desc.update({key: "" for key in body.keys()})
            elif body_type == BodyType.json:
                api_info.request.json_data.update(body)

    @staticmethod
    def merge_params(api_info: APIBodySchema, url: str):
        """
        将录制接口中的 query 参数提取后加入fastapi的params中

        :param api_info: fastapi接口数据
        :param url: 接口请求url
        :return:
        """
        parsed_url = urlparse(url)
        api_info.url = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        params = {k: v[0] for k, v in query_params.items()}
        api_info.request.params.params.update(params)
        api_info.request.params.desc.update({key: "" for key in params.keys()})

    @staticmethod
    def append_extract(
        request_data: Dict, api_info_map: Dict, item_key, item_value, request_type: str
    ):
        """
        提取引用变量，将接口中引用此变量的请求数据替换为变量值

        :param request_data: 接口请求数据, 保存格式为{"header": {...}, "request": {...}}
        :param api_info_map: 全部接口的请求信息和接口名的映射，保存格式为{"api_name": {"header": {...}, "request": {...}}
        :param item_key: 键名
        :param item_value: 键值
        :param request_type: 消息请求类型（headers, json, form, params）
        :return:
        """
        variables = CaseGenerator.extract_variables(item_value)
        if variables:
            api_name = variables[0]
            extract_var_name = variables[1]
            extract_var_path = variables[2]

            if request_type == "headers":
                CaseGenerator.replace_faster_headers(request_data, item_key, variables)
            elif request_type == "form":
                CaseGenerator.replace_faster_form(request_data, item_key, variables)
            elif request_type == "json":
                CaseGenerator.replace_faster_json(request_data, item_key, variables)
            elif request_type == "params":
                CaseGenerator.replace_faster_params(request_data, item_key, variables)
            if api_name in api_info_map:
                if {extract_var_name: extract_var_path} not in api_info_map[api_name][
                    "extract"
                ]["extract"]:
                    api_info_map[api_name]["extract"]["extract"].append(
                        {extract_var_name: extract_var_path}
                    )
                    api_info_map[api_name]["extract"]["desc"].update(
                        {extract_var_name: ""}
                    )

    @staticmethod
    def replace_faster_form(request_data: Dict, var_name: str, variables: Tuple):
        """
        替换fastapi格式请求form参数

        :param request_data:
        :param var_name:
        :param variables:
        :return:
        """
        request_data["request"]["form"]["data"].update({var_name: f"${variables[1]}"})

    @staticmethod
    def replace_faster_json(request_data: Dict, var_name: str, variables: Tuple):
        """
        替换fastapi格式请求json参数

        :param request_data:
        :param var_name:
        :param variables:
        :return:
        """
        request_data["request"]["json"].update({var_name: f"${variables[1]}"})

    @staticmethod
    def replace_faster_params(request_data: Dict, var_name: str, variables: Tuple):
        """
        替换fastapi格式请求params查询参数

        :param request_data:
        :param var_name:
        :param variables:
        :return:
        """
        request_data["request"]["params"]["params"].update(
            {var_name: f"${variables[1]}"}
        )

    @staticmethod
    def replace_faster_headers(request_data: Dict, var_name: str, variables: Tuple):
        request_data["header"]["header"].update({var_name: f"${variables[1]}"})

    @staticmethod
    def extract_field(requests: List[RequestInfo]) -> List[str]:
        """遍历接口，提取其中的变量并替换

        :param requests: 录制流量接口信息
        :return:
        """
        value_to_path_map: Dict = defaultdict(list)  # 变量值到路径的映射 {变量值: [变量路径, ...], ...}
        replaced = []  # 替换记录
        for i, item in enumerate(requests):
            if "Content-Length" in item.request_headers:
                item.request_headers.pop("Content-Length")
            if "Content-Type" in item.response_headers:
                item.response_headers.pop("Content-Type")
            # 记录变量
            CaseGenerator.record_vars(
                request=item,
                value_to_path_map=value_to_path_map,
                var_name=f"http_res_{i + 1}",
            )
            if i > 0:
                # 接口变量替换
                CaseGenerator.replace_vars(item, value_to_path_map, replaced)
        return replaced

    @staticmethod
    def replace_vars(request: RequestInfo, value_to_path_map: Dict, replaced: List):
        """
        替换变量

        :param request: 录制流量接口
        :param value_to_path_map: 记录变量值, {变量值: [变量路径, ...], ...}
        :param replaced: 替换记录
        :return:
        """
        # 提取响应内容和响应头部中的所有值
        response_values = CaseGenerator.extract_response_values(request)

        CaseGenerator.replace_url(request, value_to_path_map, replaced, response_values)
        CaseGenerator.replace_headers(
            request,
            value_to_path_map,
            replaced,
            response_values,
        )
        CaseGenerator.replace_body(
            request,
            value_to_path_map,
            replaced,
            response_values,
        )

    @staticmethod
    def extract_response_values(request: RequestInfo) -> Set:
        """
        提取响应内容和响应头部中的所有值。

        :param request: 录制流量接口
        :return: 响应值集合
        """
        response_values = set()

        # 假设响应内容是 JSON 格式的字符串，提取所有值
        if request.response_content:
            try:
                response_data = json.loads(request.response_content)
                response_values.update(
                    CaseGenerator.get_values_from_json(response_data)
                )
            except json.JSONDecodeError:
                pass

        # 添加响应头部中的所有值，除了忽略的头部键
        for key, value in request.response_headers.items():
            if key.lower() not in ignored_headers:
                response_values.add(value)

        return response_values

    @staticmethod
    def get_values_from_json(data: Union[Dict, List]) -> Set:
        """
        从 JSON 数据中递归提取所有值。

        :param data: JSON 数据，可以是字典或列表
        :return: 包含所有值的集合
        """
        values = set()
        if isinstance(data, dict):
            for value in data.values():
                values.update(CaseGenerator.get_values_from_json(value))
        elif isinstance(data, list):
            for item in data:
                values.update(CaseGenerator.get_values_from_json(item))
        else:
            values.add(data)
        return values

    @staticmethod
    def parse_url(url: str):
        """
        解析完整的URL，提取协议、域名路径和查询参数。

        :param url: 要解析的完整URL字符串。
        :return: 一个包含协议、域名路径和查询参数列表的元组。
        """
        url_parts = url.split("?")
        base_url = url_parts[0]
        query_params = url_parts[1].split("&") if len(url_parts) > 1 else []
        protocol, path_with_domain = base_url.split("//")
        return protocol, path_with_domain, query_params

    @staticmethod
    def replace_path_segments(
        path_with_domain: str,
        value_to_path_map: Dict,
        replaced: List,
        response_values: Set,
    ):
        """
        替换URL路径中的各个段落。

        :param replaced:
        :param path_with_domain: 域名和路径组合的字符串。
        :param value_to_path_map: 一个映射字典，用于替换路径中的变量。
        :param replaced: 记录替换详情的列表
        :param response_values: request_headers和request_content响应值集合
        :return: 替换后的路径段落列表。
        """
        new_url = []
        domain_and_path_list = path_with_domain.split("/")
        for segment in domain_and_path_list:
            # 检查当前字段是否是自身响应中的值，如果是则跳过
            if segment.lower() in value_to_path_map and segment not in response_values:
                new_segment = value_to_path_map[segment.lower()][0]
                new_url.append(new_segment)
                replaced.append(f"{segment} => ${new_segment}")
            else:
                new_url.append(segment)
        return new_url

    @staticmethod
    def replace_query_parameters(
        query_params: List[str],
        value_to_path_map: Dict,
        replaced: List,
        response_values: Set,
    ):
        """
        替换查询参数中的值

        :param query_params: 查询参数列表。
        :param value_to_path_map: 一个映射字典，用于替换查询参数的值。
        :param replaced: 替换后的路径段落列表。
        :return: 替换后的查询参数字符串列表。
        :param response_values: request_headers和request_content响应值集合
        """
        new_query = []
        for param in query_params:
            param_name, param_value = param.split("=")
            # 检查当前查询参数值是否是自身响应中的值，如果是则跳过
            if (
                param_value.lower() in value_to_path_map
                and param_value not in response_values
            ):
                new_param_value = value_to_path_map[param_value.lower()][0]
                new_query.append(f"{param_name}=${new_param_value}")
                replaced.append(f"{param_value} => ${new_param_value}")
            else:
                new_query.append(param)
        return new_query

    @staticmethod
    def reconstruct_url(protocol: str, new_url: List[str], new_query: List[str]):
        """
        重构URL，将协议、替换后的路径和查询参数组合成完整的URL。

        :param protocol: URL的协议部分，如 http 或 https。
        :param new_url: 经过替换的路径段落列表。
        :param new_query: 经过替换的查询参数字符串列表。
        :return: 重构后的完整URL字符串。
        """
        return f"{protocol}//{'/'.join(new_url)}{'?' + '&'.join(new_query) if new_query else ''}"

    @staticmethod
    def replace_url(
        request: RequestInfo,
        value_to_path_map: Dict,
        replaced: List,
        response_values: Set,
    ):
        """
        替换请求对象中的URL路径和查询参数。

        :param request: 包含原始URL的请求对象。
        :param value_to_path_map: 一个映射字典，用于替换URL的路径和查询参数中的值。
        :param replaced: 记录替换详情的列表。
        :param response_values: request_headers和request_content响应值集合
        :return: None。函数直接修改传入的请求对象中的URL属性。
        """
        protocol, path_with_domain, query_params = CaseGenerator.parse_url(request.url)

        new_url = CaseGenerator.replace_path_segments(
            path_with_domain,
            value_to_path_map,
            replaced,
            response_values,
        )
        new_query = CaseGenerator.replace_query_parameters(
            query_params,
            value_to_path_map,
            replaced,
            response_values,
        )

        request.url = CaseGenerator.reconstruct_url(protocol, new_url, new_query)

    @staticmethod
    def replace_headers(
        request: RequestInfo,
        value_to_path_map: Dict,
        replaced: List,
        response_values: Set,
    ):
        """
        替换请求接口中的request_headers。

        :param request: 包含原始request_headers的请求对象。
        :param value_to_path_map: 一个映射字典，用于替换request_headers的值。
        :param replaced: 记录替换详情的列表。
        :param response_values: 从响应内容和头部中提取的所有值的集合。
        :return: None。函数直接修改传入的请求对象中的request_headers属性。
        """
        for header_key, header_value in list(request.request_headers.items()):
            if header_value not in response_values:
                replacement = value_to_path_map.get(header_value)
                if replacement:
                    new_header_value = replacement[0]
                    request.request_headers[header_key] = f"${new_header_value}"
                    replaced.append(f"{header_key} => ${new_header_value}")

    @staticmethod
    def replace_body(
        request: RequestInfo,
        value_to_path_map: Dict,
        replaced: List,
        response_values: Set,
    ):
        """
        替换请求接口中的body。

        :param request: 包含原始body的请求对象。
        :param value_to_path_map: 一个映射字典，用于替换body的值。，{变量值: [变量路径, ...],...}
        :param replaced: 记录替换详情的列表。
        :param response_values: 从响应内容和头部中提取的所有值的集合。
        :return: None。函数直接修改传入的请求对象中的body属性。
        """
        if request.body:
            try:
                request_body = json.loads(request.body)
                replaced_non_str_variables = []  # 非字符串变量替换路径
                CaseGenerator.dfs_replace(
                    request_body,
                    value_to_path_map,
                    replaced_non_str_variables,
                    replaced,
                    response_values,
                )
                result = json.dumps(request_body, ensure_ascii=False)
                for v in replaced_non_str_variables:
                    result = result.replace(f"'{v}'", f"{v}")
                request.body = result
            except json.JSONDecodeError:
                pass
            except Exception as e:
                logger.error(f"转换body变量失败: {e}")

    @staticmethod
    def _dfs_replace_dict(
        request_dict: Dict,
        value_to_path_map: Dict,
        replaced_non_str_variables: List,
        replaced: List,
        response_values: Set,
    ) -> None:
        """
        递归地替换字典中的变量。

        :param request_dict: 要处理的请求体字典。
        :param value_to_path_map: 存储变量替换信息的字典。
        :param replaced_non_str_variables: 存储被替换的非字符串变量。
        :param replaced: 存储所有替换操作的列表。
        :param response_values: 从响应内容和头部中提取的所有值的集。
        :return:
        """
        for key, value in request_dict.items():
            is_str, new_value = CaseGenerator.dfs_replace(
                value,
                value_to_path_map,
                replaced_non_str_variables,
                replaced,
                response_values,
            )
            # 如果得到的替换值不是None，并且这个值不在响应值中，进行替换
            if new_value is not None and new_value not in response_values:
                request_dict[key] = f"${new_value}"
                if not is_str:
                    replaced_non_str_variables.append(f"${new_value}")

    @staticmethod
    def _dfs_replace_list(
        request_list: List,
        value_to_path_map: Dict,
        replaced_non_str_variables: List,
        replaced: List,
        response_values: Set,
    ) -> None:
        """
        递归地替换列表中的变量。

        :param request_list: 要处理的请求体列表。
        :param value_to_path_map: 存储变量替换信息的字典。
        :param replaced_non_str_variables: 存储被替换的非字符串变量。
        :param replaced: 存储所有替换操作的列表。
        :param response_values: 响应体中的值，这些值不应被替换。
        :return:
        """
        for i, item in enumerate(request_list):
            is_str, new_value = CaseGenerator.dfs_replace(
                item,
                value_to_path_map,
                replaced_non_str_variables,
                replaced,
                response_values,
            )
            if new_value is not None and new_value not in response_values:
                request_list[i] = f"${new_value}"
                if not is_str:
                    replaced_non_str_variables.append(f"${new_value}")

    @staticmethod
    def _dfs_replace_value(value, value_to_path_map, replaced, response_values):
        """
        替换基本数据类型的值。

        :param value: 要替换的值。
        :param value_to_path_map: 存储变量替换信息的字典。
        :param replaced: 存储所有替换操作的列表。
        :param response_values: 响应体中的值，这些值不应被替换。
        :return: 替换结果和是否为字符串的标志。
        """
        # 将非字符串类型的值转换为字符串以进行比较
        value_str = str(value) if not isinstance(value, str) else value

        # 如果这个值在映射中并且不在响应值中，使用映射中的新值进行替换
        if value_str in value_to_path_map and value_str not in response_values:
            new_value = value_to_path_map[value_str][0]
            replaced.append(f"{value_str} => ${new_value}")
            # 返回替换状态和新值，非字符串类型的变量也记录在replaced_non_str_variables中
            return not isinstance(value, str), new_value

        return None, None

    @staticmethod
    def dfs_replace(
        request_body: Any,
        value_to_path_map: Dict,
        replaced_non_str_variables: List,
        replaced: List,
        response_values: Set,
    ):
        """
        对请求体进行深度优先遍历，替换其中的变量。

        :param request_body: 请求体，可能是字典、列表或基本数据类型。
        :param value_to_path_map: 存储变量替换信息的字典。
        :param replaced_non_str_variables: 存储被替换的非字符串变量。
        :param replaced: 存储所有替换操作的列表。
        :param response_values: 从响应内容和头部中提取的所有值的集。
        :return:
        """

        # 处理字典类型的请求体
        if isinstance(request_body, dict):
            CaseGenerator._dfs_replace_dict(
                request_body,
                value_to_path_map,
                replaced_non_str_variables,
                replaced,
                response_values,
            )
        # 处理列表类型的请求体
        elif isinstance(request_body, list):
            CaseGenerator._dfs_replace_list(
                request_body,
                value_to_path_map,
                replaced_non_str_variables,
                replaced,
                response_values,
            )
        # 处理基本数据类型的请求体
        else:
            return CaseGenerator._dfs_replace_value(
                request_body,
                value_to_path_map,
                replaced,
                response_values,
            )

    @staticmethod
    def record_vars(request: RequestInfo, value_to_path_map: Dict, var_name: str):
        """
        记录变量
        :param request: 录制流量的接口信息
        :param value_to_path_map: 变量值到路径的映射 {变量值: [变量路径, ...], ...}
        :param var_name: http_res_{i + 1}
        :return:
        """
        CaseGenerator.split_headers(
            request,
            value_to_path_map,
            var_name,
        )
        CaseGenerator.split_body(
            request,
            value_to_path_map,
            var_name,
        )

    @staticmethod
    def split_headers(
        request: RequestInfo,
        value_to_path_map: Dict,
        var_name: str = "",
        header_path_prefix: str = "headers",
    ):
        """
        分析和记录请求头中的变量及其对应的路径。

        :param request: 包含响应头的请求信息对象。
        :param value_to_path_map: 一个映射，将变量值映射到其在请求中的路径。
        :param var_name: 用于变量提取的基本名称。
        :param header_path_prefix: 用于变量路径的前缀。
        :return:
        """
        try:
            CaseGenerator.dfs(
                request.response_headers,
                var_name,
                header_path_prefix,
                value_to_path_map,
                headers=True,
            )
        except Exception as e:
            raise GenerateError(f"解析接口headers变量出错：{e}")

    @staticmethod
    def split_body(
        request: RequestInfo,
        value_to_path_map: Dict,
        var_name: str = "",
        content_path_prefix: str = "content",
    ):
        """
        分析和记录请求体中的变量及其对应的路径。

        :param request: 包含响应内容的请求信息对象。
        :param value_to_path_map: 一个映射，将变量值映射到其在请求中的路径。
        :param var_name: 用于变量提取的基本名称。
        :param content_path_prefix: 用于变量路径的前缀。
        :return:
        """
        if request.body:
            try:
                body = json.loads(request.response_content)
                CaseGenerator.dfs(
                    body=body,
                    var_name=var_name,
                    var_path=content_path_prefix,
                    value_to_path_map=value_to_path_map,
                )
            except json.JSONDecodeError:
                # body不是JSON，跳过
                pass
            except Exception as e:
                raise GenerateError(f"解析接口body变量出错：{e}")

    @staticmethod
    def dfs_dict(
        body_dict,
        var_name,
        var_path,
        value_to_path_map,
        headers,
    ):
        """
        递归地遍历响应的头部或内容，提取并记录变量及其路径。

        :param body_dict:
        :param var_name:
        :param var_path:
        :param value_to_path_map:
        :param headers:
        :return:
        """
        for key, value in body_dict.items():
            c_name = f"{var_name}_{key}"
            c_path = f"{var_path}.{key}"
            CaseGenerator.dfs(value, c_name, c_path, value_to_path_map, headers)

    @staticmethod
    def dfs_list(body_list, var_name, var_path, value_to_path_map, headers):
        """
        递归地遍历响应的头部或内容，提取并记录变量及其路径。

        :param body_list:
        :param var_name:
        :param var_path:
        :param value_to_path_map:
        :param headers:
        :return:
        """
        for i, item in enumerate(body_list):
            c_name = f"{var_name}_{i}"
            c_path = f"{var_path}.{i}"
            CaseGenerator.dfs(item, c_name, c_path, value_to_path_map, headers)

    @staticmethod
    def process_basic_type(
        value,
        var_name,
        var_path,
        value_to_path_map,
        headers,
    ):
        """
        处理基本数据类型的值。

        :param value:
        :param var_name:
        :param var_path:
        :param value_to_path_map:
        :param headers:
        :return:
        """
        if not headers or not CaseGenerator.ignore(var_path):
            var_name_path = f"{var_name}::{var_path}"
            # 如果是bool值，需要特殊处理一下，因为Python get False/True会变成get 0 1
            if value is not None:
                if isinstance(value, bool):
                    value_to_path_map[str(value)].append(var_name_path)
                else:
                    value_to_path_map[value].append(var_name_path)

    @staticmethod
    def dfs(
        body: Any,
        var_name: str,
        var_path: str,
        value_to_path_map: Dict,
        headers: bool = False,
    ):
        """
        递归地遍历响应的头部或内容，提取并记录变量及其路径。

        :param body: 可能是响应头或响应内容的部分，可以是字典或列表。
        :param var_name: 当前变量的名称。
        :param var_path: 当前变量的提取路径。
        :param value_to_path_map: 变量到路径的映射。
        :param headers: 指示当前处理的是否是响应头。
        :return:
        """
        if isinstance(body, list):
            CaseGenerator.dfs_list(
                body,
                var_name,
                var_path,
                value_to_path_map,
                headers,
            )
        elif isinstance(body, dict):
            CaseGenerator.dfs_dict(
                body,
                var_name,
                var_path,
                value_to_path_map,
                headers,
            )
        else:
            CaseGenerator.process_basic_type(
                body,
                var_name,
                var_path,
                value_to_path_map,
                headers,
            )
