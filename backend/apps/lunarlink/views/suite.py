# -*- coding: utf-8 -*-
"""
@File    : suite.py
@Time    : 2023/2/23 15:50
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 测试用例
"""
import json
import logging

from enum import Enum
from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django_celery_beat import models as celery_models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from apps.exceptions.error import (
    ApiNotFound,
    CaseStepNotFound,
    ConfigNotFound,
    RelationNotFound,
)
from apps.schema.request import RequestInfo
from backend.utils.redis_manager import RedisHelper
from backend.utils.request_util import get_request_ip
from lunarlink import models, serializers
from lunarlink.utils import response
from lunarlink.utils import prepare
from lunarlink.utils.decorator import request_log
from lunarlink.utils.enums.TreeTypeEnum import TreeType
from lunarlink.utils.query_filters import filter_by_time_range, filter_by_node
from lunarlink.utils.request.generator import CaseGenerator


logger = logging.getLogger(__name__)


class SearchType(Enum):
    API = "2"
    CASE = "1"


tag_options = {
    "冒烟用例": 1,
    "集成用例": 2,
    "监控用例": 3,
    "核心用例": 4,
}


class TestCaseView(GenericViewSet, DestroyModelMixin):
    queryset = models.Case.objects
    serializer_class = serializers.CaseSerializer

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        """
        查询指定CASE列表

        {
            "project": int
            "node": int
        }
        """
        ser = serializers.CaseSearchSerializer(data=request.query_params)
        if ser.is_valid():
            node = ser.validated_data.get("node")
            project = ser.validated_data.get("project")
            search = ser.validated_data.get("search")
            search_type = ser.validated_data.get("searchType")
            case_type = ser.validated_data.get("caseType")
            only_me = ser.validated_data.get("onlyMe")
            creator = ser.validated_data.get("creator")
            start_time = ser.validated_data.get("start_time")
            end_time = ser.validated_data.get("end_time")

            queryset = (
                self.get_queryset().filter(project__id=project).order_by("-create_time")
            )
            # 根据创建时间过滤
            queryset = filter_by_time_range(queryset, start_time, end_time)

            if only_me is True:
                queryset = queryset.filter(creator=request.user.id)

            if creator:
                queryset = queryset.filter(creator__name=creator)

            try:
                queryset = filter_by_node(queryset, project, node, TreeType.CASE.value)
            except RelationNotFound:
                return Response(response.TREE_NOT_EXISTS)

            if case_type != "":
                queryset = queryset.filter(tag=case_type)

            if search != "":
                # 用例名称搜索
                if search_type == SearchType.CASE.value:
                    queryset = queryset.filter(name__contains=search)
                # API名称或API URL搜索
                elif search_type == SearchType.API.value:
                    case_id = self.case_step_search(search)
                    queryset = queryset.filter(pk__in=case_id)

            pagination_query = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pagination_query, many=True)

            return self.get_paginated_response(serializer.data)
        else:
            return Response(ser.errors, status=HTTP_400_BAD_REQUEST)

    @method_decorator(request_log(level="INFO"))
    def post(self, request):
        """
        新增测试用例集
        {
            length: int,
            name: str,
            project: int,
            relation: int,
            tag: str,
            body: [{
                id: int,
                name: str,
                url: str,
                method: str,
                project: int,
                relation: int,
                body: {},
                rig_env: int,
                tag: int,
                tag_name: str,
                update_time: datetime,
                is_deleted: bool,
                creator: str,
            }],
            cases: [{
                case_name: str,
                case_id: str,
            }],
            relation_name: str,
        }
        """
        project_id = int(request.data.pop("project", None))
        if not models.Project.objects.filter(id=project_id).exists():
            return Response(response.PROJECT_NOT_EXISTS)

        request.data["tag"] = tag_options[request.data["tag"]]
        step_body_list = request.data.pop("body", None)
        # 数据库事务处理
        try:
            with transaction.atomic():
                case_obj = models.Case.objects.create(
                    **request.data,
                    project_id=project_id,
                    creator=request.user,
                )
                prepare.generate_casestep(
                    step_body_list=step_body_list,
                    case_obj=case_obj,
                    creator=request.user,
                )
        except ConfigNotFound:
            return Response(response.CONFIG_NOT_EXISTS)
        except ApiNotFound:
            return Response(response.API_NOT_FOUND)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=500)

        return Response({"test_id": case_obj.id, **response.CASE_ADD_SUCCESS})

    @staticmethod
    def case_step_search(search: str):
        """
        搜索case_step的url或name
        返回对应的case_id
        """
        case_id = models.CaseStep.objects.filter(
            Q(name__contains=search) | Q(url__contains=search)
        ).values("case_id")

        case_id = set(item["case_id"] for _, item in enumerate(case_id))
        return case_id

    @method_decorator(request_log(level="INFO"))
    def patch(self, request, pk):
        """
        更新测试用例集
        {
            name: str
            id: int
            body: []
            project: int
        }
        """

        step_body_list = request.data.pop("body", None)
        try:
            case_obj = models.Case.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.CASE_NOT_EXISTS)

        try:
            prepare.update_casestep(
                step_body_list=step_body_list,
                case_obj=case_obj,
                creator=request.user,
                updater=request.user.id,
            )
        except ConfigNotFound:
            return Response(response.CONFIG_NOT_EXISTS)
        except ApiNotFound:
            return Response(response.API_NOT_FOUND)
        except CaseStepNotFound:
            return Response(response.CASE_STEP_NOT_EXIST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=500)

        request.data["tag"] = tag_options[request.data["tag"]]
        models.Case.objects.filter(id=pk).update(
            **request.data,
            update_time=timezone.now(),
            updater=request.user.id,
        )

        return Response(response.CASE_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def copy(self, request, pk):
        """复制测试用例
        pk int: test id
        {
            name: test name
            relation: int
            project: int
        }
        """
        try:
            name = request.data["name"]
        except KeyError:
            return Response(response.KEY_MISS)

        username = request.user.id
        if "|" in name:
            resp = self.split(pk, name)
        else:
            try:
                case = models.Case.objects.get(id=pk)
            except ObjectDoesNotExist:
                return Response(response.CASE_NOT_EXISTS)
            case.id = None
            case.name = name
            case.creator = request.user
            case.updater = username
            case.save()

            case_step = models.CaseStep.objects.filter(case__id=pk)

            for step in case_step:
                step.id = None
                step.case = case
                step.creator = request.user
                step.updater = username
                step.save()
            resp = response.CASE_ADD_SUCCESS

        return Response(resp)

    @method_decorator(request_log(level="INFO"))
    def destroy(self, request, pk):
        """
        单个删除

        pk: test id
        """
        case_obj = models.Case.objects.filter(id=pk).first()
        if not case_obj:
            return Response(response.CASE_NOT_EXISTS)

        # description为项目id, args为用例id
        if celery_models.PeriodicTask.objects.filter(
            args__contains=str(case_obj.id)
        ).exists():
            return Response(response.CASE_IS_USED)

        case_obj.is_deleted = True
        case_obj.updater = request.user.id
        case_obj.update_time = timezone.now()
        case_obj.save()  # 这将触发 pre_save 信号，并执行 delete_related_steps 处理器函数

        return Response(response.CASE_DELETE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def bulk_destroy(self, request, *args, **kwargs):
        """
        批量删除用例

        [
            {
                id:int
            }
        ]
        """
        ids = [content["id"] for content in request.data]
        objs = list(models.Case.objects.filter(id__in=ids))
        if not objs:
            return Response(response.CASE_NOT_EXISTS)

        unused_ids = []
        try:
            with transaction.atomic():
                for obj in objs:
                    if celery_models.PeriodicTask.objects.filter(
                        args__contains=str(obj.id)
                    ).exists():
                        continue
                    else:
                        unused_ids.append(obj.id)

                if not unused_ids:
                    return Response(response.CASE_IS_USED)

                # 批量更新待删除的用例
                models.Case.objects.filter(id__in=unused_ids).update(
                    is_deleted=True,
                    update_time=timezone.now(),
                    updater=request.user.id,
                )
                # 批量更新待删除用例的CaseStep
                models.CaseStep.objects.filter(case__in=unused_ids).update(
                    is_deleted=True,
                    update_time=timezone.now(),
                    updater=request.user.id,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response(response.CASE_DELETE_SUCCESS)

    @staticmethod
    def split(pk, name: str):
        """切割用例
        :param pk: 用例id
        :param name: 用例名称
        :return:
        """
        split_case_name = name.split("|")[0]
        split_condition = name.split("|")[1]

        # 更新原有case长度
        case = models.Case.objects.get(id=pk)
        case_step = models.CaseStep.objects.filter(
            case__id=pk, name__contains=split_condition
        )
        case_step_length = len(case_step)
        case.length -= case_step_length
        case.save()

        new_case = models.Case.objects.filter(name=split_case_name).last()
        if new_case:
            new_case.length += case_step_length
            new_case.save()
            case_step.update(case=new_case)
        else:
            # 创建一条新的case
            case.id = None
            case.name = split_case_name
            case.length = case_step_length
            case.save()

            # 把原来的case_step中的case_id改成新的case_id
            case_step.update(case=case)

        return response.CASE_SPILT_SUCCESS

    @method_decorator(request_log(level="INFO"))
    def move(self, request):
        """
        移动测试用例到其它目录
        """
        project: int = request.data.get("project")
        relation: int = request.data.get("relation")
        cases: list = request.data.get("case")
        ids = [case["id"] for case in cases]
        objs = models.Case.objects.filter(project=project, id__in=ids)
        if objs:
            objs.update(relation=relation)
        else:
            return Response(response.CASE_NOT_EXISTS)

        return Response(response.CASE_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def update_tag(self, request):
        """批量更新用例类型"""
        case_ids: list = request.data.get("case_ids", [])
        project_id: int = request.data.get("project_id", 0)
        tag: list = request.data.get("tag")
        objs = models.Case.objects.filter(project_id=project_id, pk__in=case_ids)
        if objs:
            objs.update(tag=tag)
        else:
            return Response(response.CASE_NOT_EXISTS)

        return Response(response.TAG_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def put(self, request, **kwargs):
        """
        用例步骤同步成功

        将api最新的name, body, url, method更新到用例case_step中
        pk: case_id
        """
        # case_id
        pk = kwargs.get("pk")

        # 在case_step表中找出case_id对应的所有记录，并且排除config
        api_id_list_of_dict = (
            models.CaseStep.objects.filter(case_id=pk)
            .exclude(method="config")
            .values("source_api_id", "step")
        )

        if api_id_list_of_dict:
            # 通过source_api_id找到原来的api
            # 把原来的api的name, body, url, method更新到case_step中
            for item in api_id_list_of_dict:
                source_api_id: int = item["source_api_id"]
                # 不存在api_id的直接跳过
                if source_api_id == 0:
                    continue
                step: int = item["step"]
                source_api = (
                    models.API.objects.filter(pk=source_api_id)
                    .values("name", "body", "url", "method")
                    .first()
                )
                if source_api is not None:
                    models.CaseStep.objects.filter(
                        case_id=pk, source_api_id=source_api_id, step=step
                    ).update(**source_api)
            models.Case.objects.filter(pk=pk).update(update_time=timezone.now())
        else:
            return Response(response.CASE_NOT_EXISTS)

        return Response(response.CASE_STEP_SYNC_SUCCESS)


class CaseStepView(APIView):
    """测试用例step操作视图"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request, **kwargs):
        """
        获取用例集信息

        pk: case_id
        """
        pk = kwargs.get("pk")

        queryset = models.CaseStep.objects.filter(case__id=pk).order_by("step")

        serializer = serializers.CaseStepSerializer(instance=queryset, many=True)

        try:
            case_obj = models.Case.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(response.CASE_NOT_EXISTS)

        resp = {
            "case": serializers.CaseSerializer(instance=case_obj, many=False).data,
            "step": serializer.data,
        }

        return Response(resp)


class RecordStartView(APIView):
    """开始录制接口请求"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        regex = request.query_params.get("regex")
        client_ip = request.query_params.get("ip")
        is_local_str = request.query_params.get("local", "true")  # 默认为"true"字符串
        is_local = is_local_str.lower() == "true"  # 转换字符串为布尔值
        user_id = request.user.id
        if not client_ip:
            client_ip = get_request_ip(request)

        record = RedisHelper.get_address_record(client_ip)

        if record:
            record_data = json.loads(record)
            if record_data.get("user_id", "") != user_id:
                return Response(response.RECORD_IS_RUNNING)

        RedisHelper.set_address_record(user_id, client_ip, regex, is_local)

        return Response(response.RECORD_START_SUCCESS)


class RecordStopView(APIView):
    """停止录制接口请求"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        client_ip = request.query_params.get("ip")
        if not client_ip:
            client_ip = get_request_ip(request)

        record = RedisHelper.get_address_record(client_ip)
        if record:
            record_data = json.loads(record)
            RedisHelper.remove_user_record(record_data.get("user_id", ""))

        RedisHelper.remove_address_record(client_ip)

        return Response(response.RECORD_STOP_SUCCESS)


class RecordStatusView(APIView):
    """获取录制接口请求状态"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        client_ip = request.query_params.get("ip")
        user_id = request.user.id
        if not client_ip:
            client_ip = get_request_ip(request)

        address_record = RedisHelper.get_address_record(client_ip)
        user_record = RedisHelper.get_user_record(user_id)
        is_recording = False
        regex = ""
        ip = ""
        is_local = True
        if address_record:
            record_data = json.loads(address_record)
            if record_data.get("user_id", "") == user_id:
                is_recording = True
                regex = record_data.get("regex", "")
                ip = record_data.get("ip", "")
                is_local = record_data.get("local", "")
            else:
                is_recording = False
        if user_record:
            record_data = json.loads(user_record)
            is_recording = True
            regex = record_data.get("regex", "")
            ip = record_data.get("ip", "")
            is_local = record_data.get("local", "")

        data = RedisHelper.list_record_data(user_id)
        return Response(
            dict(results=data, regex=regex, ip=ip, status=is_recording, local=is_local)
        )


class RecordRemoveView(APIView):
    """删除录制数据"""

    @method_decorator(request_log(level="INFO"))
    def get(self, request):
        index = request.query_params.get("index")
        user_id = request.user.id
        RedisHelper.remove_record_data(user_id, index)

        return Response(response.RECORD_REMOVE_SUCCESS)


class GenerateCaseView(APIView):
    """录制生成用例"""

    @method_decorator(request_log(level="INFO"))
    def post(self, request):
        case_name = request.data.get("name")
        length = request.data.get("length")
        project_id = request.data.get("project")
        case_dir = request.data.get("case_dir")
        api_dir = request.data.get("api_dir")
        config = request.data.get("config")
        raw_requests = request.data.get("requests")
        if not raw_requests:
            return Response(response.RECORD_DATA_ERROR)

        if not models.Project.objects.filter(id=project_id).exists():
            return Response(response.PROJECT_NOT_EXISTS)

        config_name = config.get("body").get("name")
        try:
            config_obj = models.Config.objects.get(
                name=config_name, project_id=project_id
            )
        except models.Config.DoesNotExist:
            return Response(response.CONFIG_NOT_EXISTS)

        requests = [RequestInfo(**item) for item in raw_requests]
        CaseGenerator.extract_field(requests)
        record_case, api_instances = CaseGenerator.generate_case(
            length=length,
            project_id=project_id,
            case_dir=case_dir,
            api_dir=api_dir,
            config=config,
            case_name=case_name,
            requests=requests,
            user=request.user.id,
        )

        record_case_dict = record_case.dict()
        step_body_list = record_case_dict.pop("body", None)
        try:
            with transaction.atomic():
                case_obj = models.Case.objects.create(
                    **record_case_dict, creator=request.user
                )
                api_ids = self.save_api_instances(api_instances)
                prepare.generate_record_casestep(
                    api_ids=api_ids,
                    body=step_body_list,
                    case_obj=case_obj,
                    config_obj=config_obj,
                    user=request.user,
                    is_generate_api=bool(api_dir),
                )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=500)

        return Response({"test_id": case_obj.id, **response.CASE_GENERATOR_SUCCESS})

    @staticmethod
    def save_api_instances(api_instances: List) -> List:
        """
        保存API实例, 提取主键id并返回
        :param api_instances:
        :return:
        """
        api_ids = []
        if api_instances:
            for instance in api_instances:
                instance.save()
                api_ids.append(instance.id)
        return api_ids


class ConvertCaseView(APIView):
    """导入har或其他用例数据文件生成用例"""

    pass
