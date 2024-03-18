# -*- coding: utf-8 -*-
"""
@File    : prepare.py
@Time    : 2023/1/16 17:02
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 
"""
import logging

from ast import literal_eval
from typing import Type

import pydash
import requests

from collections import defaultdict
from typing import Dict, List, Tuple

from django.db.models import Count, Model, F, Q
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from apps.exceptions.error import ApiNotFound, ConfigNotFound, CaseStepNotFound
from lunarlink import models
from lunarlink.utils.day import get_day, get_week, get_month
from lunarlink.utils.parser import Format


logger = logging.getLogger(__name__)


def project_init(project, creator):
    """新建项目初始化"""

    # 自动生成默认debugtalk.py
    models.Debugtalk.objects.create(project=project, creator=creator)


def get_sql_dateformat(date_type: str) -> str:
    create_time = ""
    if date_type == "week":
        create_time = "CAST(YEARWEEK(create_time, 1) AS CHAR)"
    elif date_type == "month":
        create_time = "DATE_FORMAT(create_time, '%%Y%%m')"
    elif date_type == "day":
        create_time = "DATE_FORMAT(create_time, '%%Y-%%m-%%d')"

    return create_time


def get_recent_date(date_type) -> List:
    """
    获取最近6天，6周，6月的日期
    :param date_type: day | week | month
    :return:
    """
    if date_type == "day":
        return [get_day(n) for n in range(-5, 1)]
    elif date_type == "week":
        return [get_week(n) for n in range(-5, 1)]
    elif date_type == "month":
        return [get_month(n) for n in range(-5, 1)]


def list2dict(arr: List) -> Dict:
    """
    将一个包含字典的列表转换为一个字典
    :param arr: [{create_time: xxx, counts: xxx}, ...]
    :return: {create_time: counts, ...}
    """
    keys = []
    values = []
    for value in arr:
        keys.append(str(value.get("create_time")))
        values.append(value.get("counts"))
    return dict(zip(keys, values))


def complete_list(arr: List[Dict], date_type: str) -> List:
    """获取最近6天，6周，6月的数量, 并返回一个包含6个元素的列表

    :param arr: [{create_time: xxx, counts: xxx}, ...]
    :param date_type: day | week | month
    :return: [1, 2, 3, 4, 5, 6]
    """
    mapping = list2dict(arr)  # {create_time: counts, ...}
    recent_six_date_list = get_recent_date(date_type)  # ['08-13', '08-14', ...]
    # [1, 2, 3, 4, 5, 6]
    count = [mapping.get(date, 0) for date in recent_six_date_list]
    return count


def get_project_apis(project_id) -> Tuple:
    """统计项目中手动创建和yapi导入的接口数量"""
    query = models.API.objects.filter(is_deleted=False).filter(~Q(tag=4))
    if project_id:
        query = query.filter(project_id=project_id)

    project_api_map: Dict = query.aggregate(
        用户创建=Count("pk", filter=~Q(creator__name="yapi")),
        yapi导入=Count("pk", filter=Q(creator__name="yapi")),
    )

    return list(project_api_map.keys()), list(project_api_map.values())


def aggregate_case_by_tag(project_id) -> Tuple:
    """按照分类统计项目中的用例"""
    query = models.Case.objects
    if project_id:
        query = query.filter(project_id=project_id)
    case_count: Dict = query.aggregate(
        冒烟用例=Count("pk", filter=Q(tag=1)),
        集成用例=Count("pk", filter=Q(tag=2)),
        监控用例=Count("pk", filter=Q(tag=3)),
        核心用例=Count("pk", filter=Q(tag=4)),
    )
    return list(case_count.keys()), list(case_count.values())


def aggregate_reports_by_type(project_id) -> Tuple:
    """按照类型统计项目中的报告"""
    query = models.Report.objects
    if project_id:
        query = query.filter(project_id=project_id)
    report_count: Dict = query.aggregate(
        测试=Count("pk", filter=Q(type=1)),
        异步=Count("pk", filter=Q(type=2)),
        定时=Count("pk", filter=Q(type=3)),
    )
    return list(report_count.keys()), list(report_count.values())


def aggregate_reports_by_status(project_id) -> Tuple[List, List]:
    """按照状态统计项目中的报告"""
    query = models.Report.objects
    if project_id:
        query = query.filter(project_id=project_id)
    report_count: Dict = query.aggregate(
        失败=Count("pk", filter=Q(status=0)),
        成功=Count("pk", filter=Q(status=1)),
    )

    return list(report_count.keys()), list(report_count.values())


def aggregate_reports_or_case_bydate(date_type: str, model) -> List:
    """按月和周统计报告创建数量"""
    create_time = get_sql_dateformat(date_type)
    qs = (
        model.objects.extra(select={"create_time": create_time})
        .values(
            "create_time",
        )
        .annotate(counts=Count("id"))
        .values("create_time", "counts")
    )

    # qs = [{"create_time": xxx, "counts": xxx}]
    # qs = list(qs)
    # 查询结果是按时间升序，取最后6条
    # 没有的补0
    values = complete_list(arr=qs, date_type=date_type)

    return values


def aggregate_apis_bydate(date_type: str, is_yapi=False) -> List:
    """按照日，周，月统计项目中手动创建和从yapi导入的接口数量

    :param date_type: day | week | month
    :param is_yapi: False: 统计手动创建的接口数量，True: 统计yapi导入的接口数量
    :return: 返回统计结果
    """
    create_time = get_sql_dateformat(date_type)

    query = models.API.objects.filter(~Q(tag=4))
    if is_yapi:
        query = query.filter(creator__name="yapi")
    else:
        query = query.filter(~Q(creator__name="yapi"))

    count_data = (
        query.extra(select={"create_time": create_time})
        .values(
            "create_time",
        )
        .annotate(counts=Count("id"))
        .values("create_time", "counts")
    )

    # 查询结果是按时间升序，取最后6条
    # 没有的补0
    count = complete_list(arr=count_data, date_type=date_type)

    return count


def aggregate_data_by_date(
    date_type: str, model: Type[Model]
) -> Tuple[List[str], Dict[str, List[int]]]:
    """
    按照日，周，月统计不同模型中的数据项数量。
    返回创建人列表和每个创建人在每个时间段内创建的数据项数量。

    :param date_type: day | week | month
    :param model: 数据模型
    :return: (创建人列表, 创建人所创建的数据项数量字典)
    """
    create_time = get_sql_dateformat(date_type)
    if model == models.API:
        query = model.objects.filter(~Q(tag=4), ~Q(creator__name="yapi"))
    else:
        query = model.objects

    count_data = (
        query.annotate(
            creator_name=F("creator__name"),
        )
        .extra(select={"create_time": create_time})
        .values("creator_name", "create_time")
        .annotate(counts=Count("id"))
        .order_by("creator_name", "create_time")
    )

    # 获取最近6个时间段
    recent_six_date_list = get_recent_date(date_type)

    # 获取创建人在每个时间段内创建的接口数量，并找出前5名
    creators, counts_dict = extract_top_creators_and_counts(
        count_data, recent_six_date_list
    )

    return creators, counts_dict


def extract_top_creators_and_counts(
    count_data: QuerySet,
    recent_six_date_list: List[str],
) -> Tuple[List[str], Dict[str, List[int]]]:
    """
    从聚合数据中提取创建人列表和创建人在每个时间段内创建的数据项数量，并找出前5名

    :param count_data: 统计数据
    :param recent_six_date_list: 最近6个时间段
    :return:
    """
    # 初始化计数字典
    counts_dict = defaultdict(lambda: [0] * len(recent_six_date_list))

    # 填充计数字典
    for item in count_data:
        creator = item["creator_name"]
        create_time = item["create_time"]
        if create_time in recent_six_date_list:
            date_index = recent_six_date_list.index(create_time)
            counts_dict[creator][date_index] += item["counts"]

    # 计算每个创建人的总数并排序
    total_counts = {creator: sum(counts) for creator, counts in counts_dict.items()}
    sorted_creators = sorted(total_counts, key=total_counts.get, reverse=True)[:5]

    # 仅保留前5名创建人的数据
    top_counts_dict = {creator: counts_dict[creator] for creator in sorted_creators}

    return sorted_creators, top_counts_dict


def get_daily_count(project_id, model_name, start, end):
    # 生成日期list, ['08-13', '08-14', ...]
    recent_days = [get_day(n)[5:] for n in range(start, end)]
    models_mapping = {"api": models.API, "case": models.Case, "report": models.Report}
    model = models_mapping[model_name]
    query = model.objects
    if model_name == "api":
        query = query.filter(~Q(tag=4))

    # 统计给定日期范围内，每天创建的条数
    count_data: List = (
        query.filter(
            project_id=project_id, create_time__range=[get_day(start), get_day(end)]
        )
        .extra(select={"create_time": "DATE_FORMAT(create_time,'%%m-%%d')"})
        .values("create_time")
        .annotate(counts=Count("id"))
        .values("create_time", "counts")
    )

    # list转dict，key是日期，value是统计数
    create_time_count_mapping = {
        data["create_time"]: data["counts"] for data in count_data
    }

    # 日期为空的key, 补0
    count = [create_time_count_mapping.get(d, 0) for d in recent_days]
    return {"days": recent_days, "count": count}


def get_project_daily_create(project_id) -> Dict:
    """项目每天创建的api, case, report"""
    start = -6
    end = 1
    count_mapping = {}
    for model in ("api", "case", "report"):
        count_mapping[model] = get_daily_count(
            project_id=project_id,
            model_name=model,
            start=start,
            end=end,
        )
    return count_mapping


def get_project_detail_v2(pk) -> Dict:
    """统计项目api, case, report总数和每日创建"""
    api_create_type, api_create_type_count = get_project_apis(project_id=pk)
    case_tag, case_tag_count = aggregate_case_by_tag(project_id=pk)
    report_type, report_type_count = aggregate_reports_by_type(project_id=pk)
    daily_create_count = get_project_daily_create(project_id=pk)
    res = {
        "api_count_by_create_type": {
            "type": api_create_type,
            "count": api_create_type_count,
        },
        "case_count_by_tag": {"tag": case_tag, "count": case_tag_count},
        "report_count_by_type": {"type": report_type, "count": report_type_count},
        "daily_create_count": daily_create_count,
    }
    return res


# TODO 后面需要替换成TAPD case
def get_jira_core_case_cover_rate(pk) -> Dict:
    """
    :param pk: 主键id
    :return:
    """
    project_obj = models.Project.objects.get(pk=pk)
    jira_cases = []
    if project_obj.jira_bearer_token == "" or project_obj.jira_project_key == "":
        logger.info("jira token或jira project key没配置")
    else:
        base_url = "https://jira.xxx.com/rest/api/latest/search"
        data = {
            "jql": f"project = {project_obj.jira_project_key} AND issuetpye = '测试用例'",
            "maxResults": -1,
        }
        headers = {
            "Authorization": f"Bearer {project_obj.jira_bearer_token}",
            "Content-Type": "application/json",
        }
        try:
            # TODO 分页查找所有的核心case
            res = requests.post(url=base_url, headers=headers, json=data).json()
            err = res.get("errorMessage")
            if err:
                logger.error(err)
            else:
                jira_cases.extend(res["issues"])
        except Exception as e:
            logger.error(str(e))

    jira_core_case_count = 0
    for case in jira_cases:
        if pydash.get(case, "fields.customfield_11400.value") == "是":
            jira_core_case_count += 1

    covered_case_count = len(models.Case.objects.filter(project=pk, tag=4))

    if jira_core_case_count == 0:
        core_case_cover_rate = "0.00"
    else:
        core_case_cover_rate = "%.2f" % (
            (covered_case_count / jira_core_case_count) * 100
        )

    return {
        "jira_core_case_count": jira_core_case_count,
        "core_case_count": covered_case_count,
        "core_case_cover_rate": core_case_cover_rate,
    }


def tree_end(params, project):
    """
    :param params: {
        node: int,
        type: int
    }
    :param project: Project Model
    :return:
    """
    tree_type = params["type"]
    node = params["node"]

    if tree_type == 1:
        models.API.objects.filter(relation=node, project=project).delete()

    # remove node testcase
    elif tree_type == 2:
        case = models.Case.objects.filter(relation=node, project=project).values("id")

        for case_id in case:
            models.CaseStep.objects.filter(case__id=case_id["id"]).delete()
            models.Case.objects.filter(id=case_id["id"]).delete()


def generate_record_casestep(
    api_ids: List,
    body: List,
    case_obj,
    config_obj,
    user,
    is_generate_api: bool = False,
):
    """
    生成录制测试用例步骤

    :param api_ids: 录制的api id
    :param is_generate_api:
    :param body: 测试用例步骤，包含配置和接口
    :param case_obj: 用例模型对象
    :param config_obj: 配置模型对象
    :param user: 当前用户
    :param is_generate_api: 是否同步生成api
    :return:
    """
    case_steps: List = []  # index 为测试用例步骤的执行顺序

    for index, item in enumerate(body):
        if (
            item["body"].get("method") == "config"
            or item["body"].get("request") == "config"
        ):
            name = config_obj.name
            url = config_obj.base_url
            method = "config"
            new_body = literal_eval(config_obj.body)
            source_api_id = 0  # 如果是配置默认为0
        else:
            name = item["body"]["name"]
            url = item["body"]["request"]["url"]
            method = item["body"]["request"]["method"]
            new_body = item["body"]
            # 不同步生成api，设置为-1
            source_api_id = api_ids[index - 1] if is_generate_api else -1

        kwargs = {
            "name": name,  # api接口名称或配置名称
            "body": new_body,  # api接口或配置body
            "url": url,
            "method": method,
            "step": index,
            "case": case_obj,
            "source_api_id": source_api_id,
            "creator": user,
        }
        case_step = models.CaseStep(**kwargs)
        case_steps.append(case_step)

    models.CaseStep.objects.bulk_create(objs=case_steps)


def generate_casestep(
    step_body_list: List,
    case_obj,
    creator,
):
    """
    生成用例集步骤

    :param step_body_list: 测试用例步骤，包含配置和接口
    :param case_obj: 用例模型对象
    :param creator: 当前用户
    :return:
    """
    case_steps: List = []  # index 为测试用例步骤的执行顺序
    source_api_id = 0
    for index, item in enumerate(step_body_list):
        try:
            # 进入case step 修改保存后会生成newBody字段
            format_http = Format(item["newBody"])
            format_http.parse()
            name = format_http.name
            new_body = format_http.testcase
            url = format_http.url
            method = format_http.method
        except KeyError:
            if (
                item["body"].get("method") == "config"
                or item["body"].get("request") == "config"
            ):
                name = item["body"]["name"]
                method = item["body"]["method"]
                try:
                    config = models.Config.objects.get(
                        name=name, project=case_obj.project
                    )
                except ObjectDoesNotExist:
                    raise ConfigNotFound("指定的配置不存在")
                url = config.base_url
                new_body = literal_eval(config.body)
                source_api_id = 0  # config没有api, 默认为0
            else:
                name = item["body"]["name"]
                url = item["body"]["url"]
                method = item["body"]["method"]
                try:
                    api = models.API.objects.get(id=item["id"])
                except ObjectDoesNotExist:
                    raise ApiNotFound("指定的接口不存在")
                new_body = literal_eval(api.body)

                if api.name != name:
                    new_body["name"] = name
                source_api_id = item["id"]

        kwargs = {
            "name": name,  # api接口名称或配置名称
            "body": new_body,  # api接口或配置body
            "url": url,
            "method": method,
            "step": index,
            "case": case_obj,
            "source_api_id": source_api_id,
            "creator": creator,
        }
        case_step = models.CaseStep(**kwargs)
        case_steps.append(case_step)

    models.CaseStep.objects.bulk_create(objs=case_steps)


def update_casestep(
    step_body_list: List,
    case_obj,
    creator,
    updater,
):
    """
    更新测试用例步骤

    :param step_body_list: 测试用例步骤，包含配置和接口
    :param case_obj: 用例模型对象
    :param creator: 当前用户
    :param updater: 当前用户
    :return:
    """
    step_list = list(models.CaseStep.objects.filter(case=case_obj).values("id"))

    for index, item in enumerate(step_body_list):
        try:
            # 进入case step 修改保存后会生成newBody字段
            format_http = Format(item["newBody"])
            format_http.parse()
            name = format_http.name
            new_body = format_http.testcase
            url = format_http.url
            method = format_http.method
        except KeyError:
            if "case" in item.keys():
                try:
                    case_step = models.CaseStep.objects.get(id=item["id"])
                except ObjectDoesNotExist:
                    raise CaseStepNotFound("指定的用例步骤不存在")
            elif item["body"]["method"] == "config":
                try:
                    case_step = models.Config.objects.get(
                        name=item["body"]["name"], project_id=case_obj.project_id
                    )
                except ObjectDoesNotExist:
                    raise ConfigNotFound("指定的配置不存在")
            else:
                try:
                    case_step = models.API.objects.get(id=item["id"])
                except ObjectDoesNotExist:
                    raise ApiNotFound("指定的接口不存在")

            new_body = literal_eval(case_step.body)
            name = item["body"]["name"]
            if case_step.name != name:
                new_body["name"] = name

            if item["body"]["method"] == "config":
                url = ""
                method = "config"
                source_api_id = 0  # config没有source_api_id, 默认为0
            else:
                url = item["body"]["url"]
                method = item["body"]["method"]
                source_api_id = item.get("source_api_id", 0)
                # 新增的case_step没有source_api_id字段，需要重新赋值
                if source_api_id == 0:
                    source_api_id = item["id"]
        else:
            if item.get("source_api_id", 0) == 0:
                source_api_id = item["id"]
            else:
                source_api_id = item["source_api_id"]

        kwargs = {
            "name": name,
            "body": new_body,
            "url": url,
            "method": method,
            "step": index,
            "source_api_id": source_api_id,
        }
        # is_copy 为 True表示用例步骤是复制的
        if "case" in item.keys() and item.pop("is_copy", False) is False:
            models.CaseStep.objects.filter(id=item["id"]).update(
                **kwargs, updater=updater
            )
            step_list.remove({"id": item["id"]})
        else:
            kwargs["case"] = case_obj
            models.CaseStep.objects.create(**kwargs, creator=creator)

    # 删除多余的step，获取需要删除的所有CaseStep id
    step_id_list = [content["id"] for content in step_list]
    # 使用一次查询进行更新
    models.CaseStep.objects.filter(id__in=step_id_list).update(
        is_deleted=True, update_time=timezone.now(), updater=updater
    )
