# -*- coding: utf-8 -*-
"""
@File    : serializers.py
@Time    : 2023/1/14 14:25
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 序列化&反序列化
"""


import datetime
import json
from ast import literal_eval
from typing import Union

from croniter import croniter
from django.contrib.auth import get_user_model
from django.db.models import Q
from django_celery_beat.models import PeriodicTask

from rest_framework import serializers

from lunarlink import models
from lunarlink.utils.parser import Parse
from lunarlink.utils.tree import get_tree_relation_name


Users = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    """项目信息序列化"""

    api_cover_rate = serializers.SerializerMethodField()
    creator_name = serializers.SlugRelatedField(
        slug_field="name",
        source="creator",
        read_only=True,
    )
    updater_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Project
        fields = [
            "id",
            "name",
            "desc",
            "responsible",
            "creator",
            "creator_name",
            "create_time",
            "updater",
            "updater_name",
            "update_time",
            "yapi_openapi_token",
            "yapi_base_url",
            "api_cover_rate",
            "jira_project_key",
            "jira_bearer_token",
        ]

    def get_updater_name(self, obj):
        if not hasattr(obj, "updater") or obj.updater is None:
            return None
        user = Users.objects.filter(id=obj.updater).first()
        return user.name if user else None

    def get_api_cover_rate(self, obj) -> str:
        """
        接口覆盖率，百分比保留两位小数
        :param obj: Project实例对象
        :return:
        """
        apis = (
            models.API.objects.filter(project_id=obj.id, is_deleted=False)
            .filter(~Q(tag=4))
            .values("url", "method")
        )
        api_unique = {f'{api["url"]}_{api["method"]}' for api in apis}
        case_steps = (
            models.CaseStep.objects.filter(case__project_id=obj.id)
            .filter(~Q(method="config"))
            .values("url", "method")
        )
        case_steps_unique = {
            f'{case_step["url"]}_{case_step["method"]}' for case_step in case_steps
        }
        if len(api_unique) == 0:
            return "0.00"
        if len(case_steps_unique) > len(api_unique):
            return "100.00"
        return "%.2f" % (len(case_steps_unique & api_unique) / len(api_unique) * 100)


class VisitSerializer(serializers.ModelSerializer):
    """
    访问统计序列化
    """

    class Meta:
        model = models.Visit
        fields = "__all__"


class DebugTalkSerializer(serializers.ModelSerializer):
    """
    驱动代码序列化
    """

    class Meta:
        model = models.Debugtalk
        fields = "__all__"


class RelationSerializer(serializers.ModelSerializer):
    """树形结构序列化"""

    class Meta:
        model = models.Relation
        fields = "__all_"


class AssertSerializer(serializers.Serializer):
    """API搜索序列化"""

    class Meta:
        model = models.API

    node = serializers.IntegerField(min_value=0, default=None)
    project = serializers.IntegerField(required=True, min_value=1)
    search = serializers.CharField(default="")
    creator = serializers.CharField(required=False, default="")
    tag = serializers.ChoiceField(choices=models.API.TAG, default="")
    rigEnv = serializers.ChoiceField(choices=models.API.ENV_TYPE, default="")
    is_deleted = serializers.BooleanField(default=False)
    onlyMe = serializers.BooleanField(default=False)
    showYAPI = serializers.BooleanField(default=True)
    start_time = serializers.CharField(required=False, default=None)
    end_time = serializers.CharField(required=False, default=None)


class CaseSearchSerializer(serializers.Serializer):
    """
    用例反序列化验证器
    """

    creator = serializers.CharField(required=False, default="")
    node = serializers.IntegerField(min_value=0, default=None)
    project = serializers.IntegerField(required=True, min_value=1)
    search = serializers.CharField(default="")
    searchType = serializers.CharField(default="")
    caseType = serializers.CharField(default="")
    onlyMe = serializers.BooleanField(default=False)
    start_time = serializers.CharField(required=False, default=None)
    end_time = serializers.CharField(required=False, default=None)


class CaseSerializer(serializers.ModelSerializer):
    """用例信息序列化"""

    creator_name = serializers.SlugRelatedField(
        slug_field="name",
        source="creator",
        read_only=True,
    )
    tag = serializers.CharField(source="get_tag_display")
    tasks = serializers.ListField(read_only=True)  # 包含用例的定时任务
    updater_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Case
        fields = "__all__"

    def get_updater_name(self, obj):
        if not hasattr(obj, "updater") or obj.updater is None:
            return None
        user = Users.objects.filter(id=obj.updater).first()
        return user.name if user else None


class CaseStepSerializer(serializers.ModelSerializer):
    """用例步骤序列化"""

    body = serializers.SerializerMethodField()

    class Meta:
        model = models.CaseStep
        fields = [
            "id",
            "name",
            "url",
            "method",
            "body",
            "case",
            "source_api_id",
            "creator",
            "updater",
        ]
        depth = 1

    def get_body(self, obj):
        body = literal_eval(obj.body)
        if "base_url" in body["request"].keys():
            return {"name": body["name"], "method": "config"}
        else:
            parse = Parse(literal_eval(obj.body))
            parse.parse_http()
            return parse.testcase


class APIRelatedCaseSerializer(serializers.Serializer):
    case_name = serializers.CharField(source="case.name")
    case_id = serializers.CharField(source="case.id")

    class Meta:
        fields = ["case_id", "case_name"]


class APISerializer(serializers.ModelSerializer):
    """
    接口信息序列化
    """

    creator_name = serializers.SlugRelatedField(
        slug_field="name",
        source="creator",
        read_only=True,
    )
    body = serializers.SerializerMethodField()
    tag_name = serializers.CharField(source="get_tag_display")
    cases = serializers.SerializerMethodField()
    relation_name = serializers.SerializerMethodField()
    updater_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.API
        fields = [
            "id",
            "name",
            "url",
            "method",
            "project",
            "relation",
            "body",
            "rig_env",
            "tag",
            "tag_name",
            "update_time",
            "is_deleted",
            "creator",
            "creator_name",
            "updater",
            "updater_name",
            "cases",
            "relation_name",
        ]

    def get_body(self, obj):
        parse = Parse(literal_eval(obj.body))
        parse.parse_http()
        return parse.testcase

    def get_cases(self, obj):
        case_steps = models.CaseStep.objects.filter(source_api_id=obj.id)
        cases = APIRelatedCaseSerializer(many=True, instance=case_steps)
        return cases.data

    def get_relation_name(self, obj):
        relation_obj = models.Relation.objects.get(project_id=obj.project_id, type=1)
        label = get_tree_relation_name(literal_eval(relation_obj.tree), obj.relation)
        return label

    def get_updater_name(self, obj):
        if not hasattr(obj, "updater") or obj.updater is None:
            return None
        user = Users.objects.filter(id=obj.updater).first()
        return user.name if user else None


class ConfigSerializer(serializers.ModelSerializer):
    """配置信息序列化"""

    body = serializers.SerializerMethodField()

    class Meta:
        model = models.Config
        fields = [
            "id",
            "base_url",
            "body",
            "name",
            "update_time",
            "is_default",
            "creator",
            "updater",
        ]

    def get_body(self, obj):
        parse = Parse(literal_eval(obj.body), level="config")
        parse.parse_http()
        return parse.testcase


class VariablesSerializer(serializers.ModelSerializer):
    """
    变量信息序列化
    """

    key = serializers.CharField(allow_null=False, max_length=100, required=True)
    value = serializers.CharField(allow_null=False, max_length=1024)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = models.Variables
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    """报告信息序列化"""

    creator = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    type = serializers.CharField(source="get_type_display")
    time = serializers.SerializerMethodField()
    stat = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    success = serializers.SerializerMethodField()
    ci_job_url = serializers.CharField()

    class Meta:
        model = models.Report
        fields = [
            "id",
            "name",
            "type",
            "time",
            "stat",
            "platform",
            "success",
            "creator",
            "updater",
            "ci_job_url",
        ]

    def get_time(self, obj):
        return json.loads(obj.summary)["time"]

    def get_stat(self, obj):
        return json.loads(obj.summary)["stat"]

    def get_platform(self, obj):
        return json.loads(obj.summary)["platform"]

    def get_success(self, obj):
        return json.loads(obj.summary)["success"]


def get_cron_next_execute_time(crontab_expr: str) -> int:
    """
    获取下一个符合给定cron表达式的时间，并将其转换为时间戳返回
    :param crontab_expr: cron表达式时间
    :return:
    """
    now = datetime.datetime.now()
    cron = croniter(crontab_expr, now)
    next_time: datetime.datetime = cron.get_next(datetime.datetime)
    return int(next_time.timestamp())


class PeriodicTaskSerializer(serializers.ModelSerializer):
    """
    定时任务信息序列化
    """

    kwargs = serializers.SerializerMethodField()
    args = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    last_run_at = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTask
        fields = [
            "id",
            "name",
            "args",
            "kwargs",
            "enabled",
            "date_changed",
            "enabled",
            "description",
            "total_run_count",
            "last_run_at",
        ]

    def get_name(self, obj):
        """
        兼容定时任务名称必须唯一

        :param obj:
        :return:
        """
        name: str = obj.name
        return name.split("_")[1]

    def get_kwargs(self, obj):
        kwargs = json.loads(obj.kwargs)
        if obj.enabled:
            kwargs["next_execute_time"] = get_cron_next_execute_time(kwargs["crontab"])

        kwargs["ci_project_ids"] = kwargs.get("ci_project_ids", "")
        kwargs["ci_env"] = kwargs.get("ci_env", "请选择")
        kwargs["config"] = kwargs.get("config", "请选择")
        # False:串行，True:并行
        kwargs["is_parallel"] = kwargs.get("is_parallel", False)
        return kwargs

    def get_args(self, obj):
        case_id_list = json.loads(obj.args)
        # 数据格式, list of dict: [{"id":case_id, "name"}]
        return list(
            models.Case.objects.filter(pk__in=case_id_list).values("id", "name")
        )

    def get_last_run_at(self, obj) -> Union[str, int]:
        if obj.last_run_at:
            return int(obj.last_run_at.timestamp())
        return ""


class ScheduleDeSerializer(serializers.Serializer):
    """
    定时任务反序列化
    """

    switch = serializers.BooleanField(required=True, help_text="定时任务开关")
    crontab = serializers.CharField(
        required=True, help_text="定时任务表达式", max_length=100, allow_blank=True
    )
    ci_project_ids = serializers.CharField(
        required=True,
        allow_blank=True,
        help_text="Gitlab的项目id，多个用逗号分开，一个项目id对应多个task，但只能在同一个项目中",
    )
    strategy = serializers.CharField(required=True, help_text="发送通知策略", max_length=20)
    receiver = serializers.CharField(
        required=True, help_text="邮件接收者列表", allow_blank=True, max_length=100
    )
    mail_cc = serializers.CharField(
        required=True, help_text="邮件抄送列表", allow_blank=True, max_length=100
    )
    name = serializers.CharField(required=True, help_text="定时任务名称", max_length=100)
    webhook = serializers.CharField(
        required=True,
        help_text="飞书/企微/钉钉webhook url",
        trim_whitespace=True,
        allow_blank=True,
        max_length=500,
    )
    updater = serializers.CharField(
        required=False,
        help_text="更新人",
        max_length=20,
        allow_null=True,
        allow_blank=True,
    )
    creator = serializers.CharField(
        required=False,
        help_text="创建人",
        max_length=20,
        allow_null=True,
        allow_blank=True,
    )
    data = serializers.ListField(required=True, help_text="用例id")
    project = serializers.IntegerField(
        required=True, help_text="测试平台的项目id", min_value=1
    )

    def validate_crontab(self, value):
        """
        检查cron表达式是否有效
        """
        if not croniter.is_valid(value):
            raise serializers.ValidationError("无效的 cron 表达式")
        return value

    def validate_ci_project_ids(self, ci_project_ids):
        if ci_project_ids:
            not_allowed_project_ids = set()
            kwargs_list = PeriodicTask.objects.filter(
                ~Q(description=self.initial_data["project"])
            ).values("kwargs")
            for kwargs in kwargs_list:
                not_allowed_project_id: str = json.loads(kwargs["kwargs"]).get(
                    "ci_project_ids", ""
                )
                if not_allowed_project_id:
                    not_allowed_project_ids.update(not_allowed_project_id.split(","))

            validation_errors = set()
            for ci_project_id in ci_project_ids.split(","):
                if ci_project_id in not_allowed_project_ids:
                    validation_errors.add(ci_project_id)

            if validation_errors:
                raise serializers.ValidationError(
                    f"{','.join(validation_errors)} 已经在其他项目存在"
                )


class CISerializer(serializers.Serializer):
    """持续集成序列化"""

    ci_job_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="gitlab-ci job id",
    )
    ci_job_url = serializers.CharField(required=True, max_length=500)
    ci_pipeline_id = serializers.IntegerField(required=True)
    ci_pipeline_url = serializers.CharField(required=True, max_length=500)
    ci_project_id = serializers.IntegerField(required=True, min_value=1)
    ci_project_name = serializers.CharField(required=True, max_length=100)
    ci_project_namespace = serializers.CharField(required=False, max_length=100)
    start_job_user = serializers.CharField(
        required=True,
        max_length=100,
        help_text="GITLAB_USER_NAME",
    )


class CIReportSerializer(serializers.Serializer):
    """持续集成报告序列化"""

    ci_job_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="gitlab-ci job id",
    )
