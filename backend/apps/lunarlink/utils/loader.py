# -*- coding: utf-8 -*-
"""
@File    : loader.py
@Time    : 2023/1/16 15:27
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""
import concurrent.futures
import copy
import datetime
import importlib
import json
import logging
import os
import shutil
import sys
import time
import types
import tempfile
from ast import literal_eval
from typing import Dict, List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from requests.utils import dict_from_cookiejar
from requests.cookies import RequestsCookieJar

from backend.settings import BASE_DIR
from lunarlink import models
from lunarlink.utils.parser import Format
from lunarlink.views.report import ConvertRequest
from httprunner import HttpRunner
from apps.exceptions.error import (
    ApiNotFound,
    ConfigNotFound,
    CaseStepNotFound,
)

logger = logging.getLogger(__name__)

TEST_NOTE_EXISTS = {
    "code": "0102",
    "status": False,
    "msg": "节点下没有接口或用例集",
}


def is_function(tup: Tuple) -> bool:
    """
    判断元组内的对象是否为function, 真返回True, 否返回False
    :param tup:
    :return:
    """
    name, item = tup
    return isinstance(item, types.FunctionType)


def is_variable(tup: Tuple):
    """
    Takes (name, object) tuple, returns True if it is a variable.
    :param tup:
    :return:
    """
    name, item = tup
    if callable(item):
        # function or class
        return False

    if isinstance(item, types.ModuleType):
        # imported module
        return False

    if name.startswith("_"):
        # private property
        return False

    return True


class FileLoader:
    @staticmethod
    def dump_python_file(python_file, data):
        """dump python file"""
        with open(python_file, "w", encoding="utf-8") as stream:
            stream.write(data)

    @staticmethod
    def load_python_module(file_path):
        """load python module.

        :param file_path: python path
        :return:
            dict: variables and functions mapping for specified python module

                {
                    "variables": {},
                    "functions": {}
                }
        """
        debugtalk_module = {"variables": {}, "functions": {}}
        debugtalk_module_name = "debugtalk"
        # 修复切换项目后，debugtalk 有缓存
        if sys.modules.get(debugtalk_module_name):
            del sys.modules[debugtalk_module_name]
        sys.path.insert(0, file_path)
        module = importlib.import_module(debugtalk_module_name)
        # 修复重载bug
        importlib.reload(module)
        sys.path.pop(0)

        for name, item in vars(module).items():
            if is_function((name, item)):
                debugtalk_module["functions"][name] = item
            elif is_variable((name, item)):
                if isinstance(item, tuple):
                    continue
                debugtalk_module["variables"][name] = item
            else:
                pass

        return debugtalk_module


def load_debugtalk(project: int):
    """
    import debugtalk.py in sys.path and reload
    :param project:
    :return:
    """
    # debugtalk.py
    code = models.Debugtalk.objects.get(project__id=project).code

    tempfile_path = tempfile.mkdtemp(
        prefix="LunarLink", dir=os.path.join(BASE_DIR, "tempWorkDir")
    )
    file_path = os.path.join(tempfile_path, "debugtalk.py")
    os.chdir(tempfile_path)
    try:
        FileLoader.dump_python_file(file_path, code)
        debugtalk = FileLoader.load_python_module(os.path.dirname(file_path))
        return debugtalk, file_path
    except Exception as e:
        logger.error(e)
        os.chdir(BASE_DIR)  # 递归删除文件夹下的所有子文件夹和子文件
        shutil.rmtree(os.path.dirname(file_path))


def parse_tests(
    testcases: List,
    debugtalk: Dict,
    name=None,
    config=None,
    project=None,
):
    """
    get test case structure

    :param testcases:
    :param debugtalk: 驱动代码
    :param name:
    :param config: 配置文件
    :param project:
    :return:
    """

    refs = {
        "env": {},
        "def-api": {},
        "def-testcase": {},
        "debugtalk": debugtalk,
    }

    test_set = {
        "config": {"name": testcases[-1]["name"], "variables": []},
        "teststeps": testcases,
    }

    if config:
        test_set["config"] = config

    if name:
        test_set["config"]["name"] = name

    # 获取当前项目的全局变量
    global_variables = (
        models.Variables.objects.filter(project=project).all().values("key", "value")
    )
    # 并集，重复内容只保留一个
    all_config_variables_keys = set().union(
        *(d.keys() for d in test_set["config"].setdefault("variables", []))
    )
    global_variables_list_of_dict = []
    for item in global_variables:
        if item["key"] not in all_config_variables_keys:
            global_variables_list_of_dict.append({item["key"]: item["value"]})

    # 有 variables 就直接 extend，没有就加一个[], 再 extend
    # 配置的 variables 和全局变量重叠，优先使用配置中的 variables
    test_set["config"].setdefault("variables", []).extend(global_variables_list_of_dict)
    test_set["config"]["refs"] = refs

    # 配置中的变量和全局变量合并
    variables_mapping = {}
    if config:
        for variables in config["variables"]:
            variables_mapping.update(variables)

    return test_set


def debug_api(
    api: Union[Dict, List],
    project: int,
    name=None,
    config=None,
    save=True,
    user=None,
):
    """
    调式接口

    :param api:
    :param project:
    :param name:
    :param config:
    :param save:
    :param user:
    :return:
    """

    if len(api) == 0:
        return TEST_NOTE_EXISTS

    # testcase
    if isinstance(api, dict):
        """
        httprunner scripts or teststeps
        """
        api = [api]

    # 参数化参数过滤，只加载api中调用到的参数
    if config and config.get("parameters"):
        api_params = []
        for item in api:
            params = (
                item["request"].get("params", {})
                or item["request"].get("json", {})
                or item["request"].get("data", {})
            )
            for v in params.values():
                if isinstance(v, list):
                    api_params.extend(v)
                else:
                    api_params.append(v)
        parameters = []
        for value in config["parameters"]:
            for key in value.keys():
                # key可能是key-key1这种模式, 所以需要分割
                for i in key.split("-"):
                    if "$" + i in api_params:
                        parameters.append(value)
                        break

        config["parameters"] = parameters

    debugtalk = load_debugtalk(project=project)
    debugtalk_content = debugtalk[0]
    debugtalk_path = debugtalk[1]
    os.chdir(os.path.dirname(debugtalk_path))
    try:
        testcase_list = [
            parse_tests(
                testcases=api,
                debugtalk=debugtalk_content,
                name=name,
                config=config,
                project=project,
            )
        ]

        kwargs = {"failfast": False}
        runner = HttpRunner(**kwargs)
        runner.run(path_or_testcases=testcase_list)
        summary = parse_summary(summary=runner.summary)

        if save:
            # 保存报告信息
            save_summary(
                name=name,
                summary=summary,
                project=project,
                report_type=1,
                user=user,
            )

        # 复制一份 response 的 json
        for details in summary.get("details", []):
            for record in details.get("records", []):
                json_data = record["meta_data"]["response"].pop("json", {})
                if json_data:
                    record["meta_data"]["response"]["jsonCopy"] = json_data
        ConvertRequest.generate_curl(report_details=summary["details"])
        return summary
    except Exception as e:
        logger.error(f"debug_api error")
        raise SyntaxError(str(e))
    finally:
        os.chdir(BASE_DIR)
        shutil.rmtree(os.path.dirname(debugtalk_path))


def debug_suite(
    suite,
    project,
    obj,
    config=None,
    save=True,
    user=None,
    report_type=1,
    report_name="",
    allow_parallel=False,
):
    """debug suite

    :param suite: list[list[dict]], 用例列表
    :param project: int, 项目id
    :param obj: list[dict] [{"id": int "name": str}], 用例的名称和id
    :param config: list[dict], 每个用例运行的配置
    :param save:
    :param user:
    :param report_type: int, 默认类型是调试
    :param report_name:
    :param allow_parallel: bool, 是否允许并行
    :return:
    """
    if len(suite) == 0:
        return TEST_NOTE_EXISTS, 0

    debugtalk = load_debugtalk(project=project)
    debugtalk_content = debugtalk[0]
    debugtalk_path = debugtalk[1]
    os.chdir(os.path.dirname(debugtalk_path))

    # 先记录配置的名称，parse_tests会改变config
    config_name_list = [d["name"] for d in config]

    try:
        test_sets = create_test_sets(
            suite=suite,
            obj=obj,
            debugtalk_content=debugtalk_content,
            config=config,
            project=project,
        )

        if allow_parallel:
            summary = debug_suite_parallel(test_sets)
        else:
            kwargs = {"failfast": False}
            runner = HttpRunner(**kwargs)
            runner.run(test_sets)
            summary = parse_summary(runner.summary)

        # 统计用例级别的数据
        summary = update_summary(
            obj=obj,
            test_sets=test_sets,
            project=project,
            summary=summary,
            config_name_list=config_name_list,
        )

        report_id = 0
        if save:
            report_id = save_summary(
                name=report_name or f"批量运行{len(test_sets)}条用例",
                summary=summary,
                project=project,
                report_type=report_type,
                user=user,
            )
        # 复制一份response的json
        summary = process_response_json(summary)
        return summary, report_id
    except Exception as e:
        raise SyntaxError(str(e))
    finally:
        os.chdir(BASE_DIR)
        shutil.rmtree(os.path.dirname(debugtalk_path))


def create_test_sets(suite, obj, debugtalk_content, config, project):
    """根据给定的 suite, debugtalk_content, config 和 project，创建 test_sets
    :param obj:
    :param suite:
    :param debugtalk_content:
    :param config:
    :param project:
    :return:
    """
    test_sets = []
    for index in range(len(suite)):
        # copy.deepcopy 修复引用bug
        testcases = copy.deepcopy(
            parse_tests(
                testcases=suite[index],
                debugtalk=debugtalk_content,
                name=obj[index]["name"],
                config=config[index],
                project=project,
            )
        )
        test_sets.append(testcases)
    return test_sets


def update_summary(obj, test_sets, project, summary, config_name_list):
    """
    根据给定的 summary, config_name_list 和 details，更新 summary。
    """
    details: List = summary["details"]
    failure_case_config_mapping_list = []
    for index, detail in enumerate(details):
        if detail["success"] is False:
            # 用例失败时, 记录用例执行的配置
            failure_case_config = {"config_name": config_name_list[index]}
            failure_case_config.update(obj[index])
            failure_case_config_mapping_list.append(failure_case_config)
    case_count = len(test_sets)
    case_fail_rate = f"{len(failure_case_config_mapping_list) / case_count:.2%}"
    summary["stat"].update(
        {
            "failure_case_config_mapping_list": failure_case_config_mapping_list,
            "case_count": case_count,
            "case_fail_rate": case_fail_rate,
            "project": project,
        }
    )
    return summary


def process_response_json(summary):
    """
    处理 summary 中的 response json，以便在 summary 中添加 jsonCopy。
    """
    for _details in summary.get("details", []):
        for record in _details.get("records", []):
            json_data = record["meta_data"]["response"].pop("json", {})
            if json_data:
                record["meta_data"]["response"]["jsonCopy"] = json_data
    return summary


def debug_suite_parallel(test_sets: List):
    """
    并行运行用例
    :param test_sets:
    :return:
    """

    def run_test(test_set: Dict):
        kwargs = {"failfast": False}
        runner = HttpRunner(**kwargs)
        runner.run([test_set])
        return parse_summary(runner.summary)

    start = time.time()
    # 限制最多10个线程
    workers = min(len(test_sets), 10)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(run_test, t): t for t in test_sets}
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    duration = time.time() - start
    return merge_parallel_result(results, duration)


def merge_parallel_result(results: List, duration: float):
    """
    合并并行的结果，保持和串行的运行结果一致
    :param results: 用例执行结果
    :param duration: 用例执行时间
    :return:
    """
    base_result: Dict = results.pop()
    for result in results:
        base_result["success"] = result["success"] and base_result["success"]
        for k, v in base_result["stat"].items():
            base_result["stat"][k] = v + result["stat"][k]

        for k, v in base_result["time"].items():
            if k == "start_at":
                base_result["time"][k] = min(v, result["time"][k])
            else:
                base_result["time"][k] = v + result["time"][k]
        base_result["details"].extend(result["details"])
    base_result["time"]["duration"] = duration

    # 删除多余的key
    keys = list(base_result.keys())
    for k in keys:
        if k not in ("success", "stat", "time", "platform", "details"):
            base_result.pop(k)
    return base_result


def parse_summary(summary):
    """序列化summary
    :param summary:
    :return:
    """

    for detail in summary["details"]:
        for record in detail["records"]:
            for key, value in record["meta_data"]["request"].items():
                if isinstance(value, bytes):
                    record["meta_data"]["request"][key] = value.decode("utf-8")
                if isinstance(value, RequestsCookieJar):
                    record["meta_data"]["request"][key] = dict_from_cookiejar(value)

            for key, value in record["meta_data"]["response"].items():
                if isinstance(value, bytes):
                    record["meta_data"]["response"][key] = value.decode("utf-8")
                if isinstance(value, RequestsCookieJar):
                    record["meta_data"]["response"][key] = dict_from_cookiejar(value)

            if "text/html" in record["meta_data"]["response"]["content_type"]:
                record["meta_data"]["response"]["content"] = BeautifulSoup(
                    record["meta_data"]["response"]["content"], features="html.parser"
                ).prettify()

            if record["status"] == "failure":
                record["meta_data"].update({"validators": []})

    return summary


def save_summary(name, summary, project, report_type=2, user=None, ci_metadata=None):
    """保存报告信息"""

    if ci_metadata is None:
        ci_metadata = {}

    if "status" in summary.keys():
        return

    if name == "" or name is None:
        name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 需要先复制一份，不然会影响debug_api返回给前端的报告
    summary = copy.deepcopy(summary)
    summary_detail = summary.pop("details")
    report = models.Report.objects.create(
        **{
            "project": models.Project.objects.get(id=project),
            "name": name,
            "type": report_type,
            "status": summary["success"],
            "summary": json.dumps(summary, ensure_ascii=False),
            "creator_id": user,
            "ci_metadata": ci_metadata,
            "ci_project_id": ci_metadata.get("ci_project_id"),
            "ci_job_id": ci_metadata.get("ci_job_id", None),
        }
    )

    models.ReportDetail.objects.create(
        summary_detail=summary_detail,
        report=report,
    )

    return report.id


def load_test(test, project=None):
    """
    格式化测试用例
    :param test:
    :param project:
    :return:
    """
    try:
        format_http = Format(test["newBody"])
        format_http.parse()
        testcase = format_http.testcase
    except KeyError:
        if "case" in test.keys():
            if test["body"]["method"] == "config":
                try:
                    case_step = models.Config.objects.get(
                        name=test["body"]["name"], project=project
                    )
                except ObjectDoesNotExist:
                    raise ConfigNotFound("指定的配置不存在")
            else:
                try:
                    case_step = models.CaseStep.objects.get(id=test["id"])
                except ObjectDoesNotExist:
                    raise CaseStepNotFound("指定的用例步骤不存在")
        else:
            if test["body"]["method"] == "config":
                try:
                    case_step = models.Config.objects.get(
                        name=test["body"]["name"], project=project
                    )
                except ObjectDoesNotExist:
                    raise ConfigNotFound("指定的配置不存在")
            else:
                try:
                    case_step = models.API.objects.get(id=test["id"])
                except ObjectDoesNotExist:
                    raise ApiNotFound("指定的接口不存在")
        testcase = literal_eval(case_step.body)
        name = test["body"]["name"]

        if case_step.name != name:
            testcase["name"] = name

    return testcase
