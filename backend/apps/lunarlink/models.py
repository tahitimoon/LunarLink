from ast import literal_eval

import jsonfield
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from model_utils import Choices

from backend import settings


# Create your models here.
class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()

    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class BaseTable(models.Model):
    """
    公共字段
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"

    create_time = models.DateTimeField(
        verbose_name="创建时间", auto_now_add=True, help_text="创建时间"
    )
    update_time = models.DateTimeField(
        verbose_name="更新时间", auto_now=True, help_text="更新时间"
    )
    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_query_name="creator_query",
        null=True,
        verbose_name="创建人",
        help_text="创建人",
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    updater = models.IntegerField(
        verbose_name="修改人",
        null=True,
        help_text="修改人",
    )
    is_deleted = models.BooleanField(verbose_name="是否删除", default=False)

    objects = SoftDeleteManager()


class Project(BaseTable):
    """项目信息表"""

    class Meta:
        verbose_name = "项目信息"
        verbose_name_plural = "项目信息"
        db_table = "project"

    name = models.CharField(
        verbose_name="项目名称", null=False, max_length=100, help_text="项目名称"
    )
    desc = models.CharField(
        verbose_name="简要介绍", max_length=100, null=False, help_text="简要介绍"
    )
    responsible = models.CharField(
        verbose_name="负责人", max_length=20, null=False, help_text="负责人"
    )
    yapi_base_url = models.CharField(
        verbose_name="yapi的openapi url",
        max_length=100,
        null=False,
        default="",
        blank=True,
        help_text="yapi的openapi url",
    )
    yapi_openapi_token = models.CharField(
        verbose_name="yapi openapi的token",
        max_length=128,
        null=False,
        default="",
        blank=True,
        help_text="yapi openapi的token",
    )
    jira_project_key = models.CharField(
        verbose_name="jira项目key",
        null=False,
        default="",
        max_length=30,
        blank=True,
        help_text="jira项目key",
    )
    jira_bearer_token = models.CharField(
        verbose_name="jira bearer_token",
        null=False,
        default="",
        max_length=45,
        blank=True,
        help_text="jira bearer_token",
    )
    groups = models.ManyToManyField(
        to=Group, verbose_name="分组", help_text="这个项目所属的分组", blank=True
    )


@receiver(pre_save, sender=Project)
def delete_related_objects(sender, instance, **kwargs):
    if instance.is_deleted:
        related_models = [
            Config,
            API,
            Case,
            HostIP,
            Variables,
            Report,
            Debugtalk,
            Relation,
        ]  # 所有与 Project 直接关联的模型

        # 先筛选出要删除的对象
        case_objects = Case.objects.filter(project=instance)
        report_objects = Report.objects.filter(project=instance)

        for related_model in related_models:
            related_model.objects.filter(project=instance).update(is_deleted=True)

        PeriodicTask.objects.filter(description=instance.id).delete()

        # 注意：这部分操作可能会很慢，如果有大量的数据，考虑性能问题
        ReportDetail.objects.filter(report__in=report_objects).update(is_deleted=True)
        CaseStep.objects.filter(case__in=case_objects).update(
            is_deleted=True,
            updater=instance.updater,
            update_time=timezone.now(),
        )


class Config(BaseTable):
    """环境信息表"""

    class Meta:
        verbose_name = "环境信息"
        db_table = "config"

    name = models.CharField(verbose_name="环境名称", null=False, max_length=100)
    body = models.TextField(verbose_name="主体信息", null=False)
    base_url = models.CharField(verbose_name="请求地址", null=False, max_length=100)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )
    is_default = models.BooleanField("默认配置", default=False)


class API(BaseTable):
    """
    API信息表
    """

    class Meta:
        verbose_name = "接口信息"
        db_table = "api"

    ENV_TYPE = ((0, "测试环境"), (1, "生产环境"), (2, "预发布环境"))
    TAG = Choices(
        (0, "未知"),
        (1, "成功"),
        (2, "失败"),
        (3, "自动成功"),
        (4, "废弃"),
    )
    name = models.CharField(
        verbose_name="接口名称", null=False, max_length=100, db_index=True
    )
    body = models.TextField(verbose_name="主体信息", null=False)
    url = models.CharField(
        verbose_name="请求地址", null=False, max_length=255, db_index=True
    )
    method = models.CharField(verbose_name="请求方式", null=False, max_length=10)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )
    relation = models.IntegerField(verbose_name="节点id", null=False)
    rig_id = models.IntegerField(verbose_name="网关API_id", null=True, db_index=True)
    rig_env = models.IntegerField(verbose_name="网关环境", choices=ENV_TYPE, default=0)
    tag = models.IntegerField(verbose_name="API标签", choices=TAG, default=0)
    yapi_catid = models.IntegerField(verbose_name="yapi的分组id", null=True, default=0)
    yapi_id = models.IntegerField(verbose_name="yapi的id", null=True, default=0)
    yapi_add_time = models.CharField(
        verbose_name="yapi创建时间", null=True, default="", max_length=10
    )
    yapi_up_time = models.CharField(
        verbose_name="yapi更新时间", null=True, default="", max_length=10
    )
    yapi_username = models.CharField(
        verbose_name="yapi的原作者", null=True, default="", max_length=30
    )


class Case(BaseTable):
    """
    用例信息表
    """

    class Meta:
        verbose_name = "用例信息"
        db_table = "case"

    tag = (
        (1, "冒烟用例"),
        (2, "集成用例"),
        (3, "监控用例"),
        (4, "核心用例"),
    )
    name = models.CharField(verbose_name="用例名称", null=False, max_length=100)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )
    relation = models.IntegerField(verbose_name="节点id", null=False)
    length = models.IntegerField(verbose_name="API个数", null=False)
    tag = models.IntegerField(verbose_name="用例标签", choices=tag, default=2)

    @property
    def tasks(self):
        task_objs = PeriodicTask.objects.filter(description=self.project.id).values(
            "id",
            "name",
            "args",
        )

        def process_task(task):
            # 处理每个任务的name字段
            name_parts = task["name"].split("_")
            if len(name_parts) > 1:
                task["name"] = name_parts[1]
            return task

        # 过滤并处理任务
        processed_tasks = [
            process_task(task)
            for task in task_objs
            if self.id in literal_eval(task.pop("args"))
        ]

        return processed_tasks


@receiver(pre_save, sender=Case)
def delete_related_steps(sender, instance, **kwargs):
    """
    当一个 Case 对象被删除时，删除所有与其相关的 CaseStep 对象。
    """
    CaseStep.objects.filter(case=instance).update(
        is_deleted=True, update_time=timezone.now()
    )


class CaseStep(BaseTable):
    """
    测试用例 Step.
    """

    class Meta:
        verbose_name = "用例信息 Step"
        db_table = "case_step"

    name = models.CharField(verbose_name="用例名称", null=False, max_length=100)
    body = models.TextField(verbose_name="主体信息", null=False)
    url = models.CharField(verbose_name="请求地址", null=False, max_length=255)
    method = models.CharField(verbose_name="请求方式", null=False, max_length=10)
    case = models.ForeignKey(to=Case, on_delete=models.CASCADE, db_constraint=False)
    step = models.IntegerField(verbose_name="顺序", null=False)
    source_api_id = models.IntegerField(verbose_name="api来源", null=False)


class HostIP(BaseTable):
    """Host配置"""

    class Meta:
        verbose_name = "HOST配置"
        db_table = "host_ip"

    name = models.CharField(verbose_name="host名称", null=False, max_length=100)
    value = models.TextField(verbose_name="值", null=False)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )


class Variables(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "全局变量"
        db_table = "variables"

    key = models.CharField(verbose_name="变量名", null=False, max_length=100)
    value = models.CharField(verbose_name="变量值", null=False, max_length=1024)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )
    description = models.CharField(verbose_name="全局变量描述", null=True, max_length=100)


class Debugtalk(BaseTable):
    """
    驱动代码表
    """

    class Meta:
        verbose_name = "驱动库"
        db_table = "debugtalk"

    code = models.TextField(
        verbose_name="python代码",
        default="# write you code",
        null=False,
        help_text="python代码",
    )
    project = models.OneToOneField(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )


class Report(BaseTable):
    """报告存储"""

    report_type = (
        (1, "调试"),
        (2, "异步"),
        (3, "定时"),
        (4, "部署"),
    )

    report_status = (
        (0, "失败"),
        (1, "成功"),
    )

    class Meta:
        verbose_name = "测试报告"
        db_table = "report"

    name = models.CharField(
        verbose_name="报告名称",
        null=False,
        max_length=100,
    )
    type = models.IntegerField(
        verbose_name="报告类型",
        choices=report_type,
    )
    status = models.BooleanField(
        verbose_name="报告状态",
        choices=report_status,
        blank=True,
    )
    summary = models.TextField(verbose_name="报告基础信息", null=False)
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    ci_metadata = jsonfield.JSONField()
    ci_project_id = models.IntegerField(
        verbose_name="gitlab的项目id",
        default=0,
        null=True,
        db_index=True,
    )
    ci_job_id = models.CharField(
        verbose_name="gitlab的项目id",
        unique=True,
        null=True,
        default=None,
        db_index=True,
        max_length=15,
    )

    @property
    def ci_job_url(self):
        if self.ci_metadata:
            return self.ci_metadata.get("ci_job_url")


@receiver(pre_save, sender=Report)
def delete_related_report_detail(sender, instance, **kwargs):
    """
    当一个 Report 对象被删除时，删除所有与其相关的 ReportDetail 对象。
    """
    ReportDetail.objects.filter(report=instance).update(is_deleted=True)


class ReportDetail(models.Model):
    """报告详情"""

    class Meta:
        verbose_name = "测试报告详情"
        db_table = "report_detail"

    report = models.OneToOneField(
        to=Report,
        on_delete=models.CASCADE,
        null=True,
        db_constraint=False,
    )
    summary_detail = models.TextField(verbose_name="报告详细信息")
    is_deleted = models.BooleanField(verbose_name="是否删除", default=False)

    objects = SoftDeleteManager()


class Relation(models.Model):
    """树形结构关系"""

    class Meta:
        verbose_name = "树形结构关系"
        db_table = "relation"

    tree = models.TextField(verbose_name="结构主体", null=False, default=[])
    type = models.IntegerField(verbose_name="树类型", default=1)
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, db_constraint=False
    )
    is_deleted = models.BooleanField(verbose_name="是否删除", default=False)

    objects = SoftDeleteManager()


class Visit(models.Model):
    METHODS = Choices(
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("PATCH", "PATCH"),
        ("DELETE", "DELETE"),
        ("OPTION", "OPTION"),
    )

    class Meta:
        db_table = "visit"

    user = models.CharField(verbose_name="访问url的用户名", max_length=100, db_index=True)
    ip = models.CharField(verbose_name="用户的ip", max_length=20, db_index=True)
    project = models.CharField(
        verbose_name="项目id", max_length=4, db_index=True, default=0
    )
    url = models.CharField(verbose_name="被访问的url", max_length=255, db_index=True)
    path = models.CharField(
        verbose_name="被访问的接口路径", max_length=100, default="", db_index=True
    )
    request_params = models.CharField(
        verbose_name="请求参数", max_length=255, default="", db_index=True
    )
    request_method = models.CharField(
        verbose_name="请求方法", max_length=7, choices=METHODS, db_index=True
    )
    request_body = models.TextField(verbose_name="请求体")
    create_time = models.DateTimeField(
        verbose_name="创建时间", auto_now_add=True, db_index=True
    )


class LoginLog(BaseTable):
    LOGIN_TYPE_CHOICES = ((1, "普通登录"),)
    name = models.CharField(
        max_length=20,
        verbose_name="登录用户姓名",
        null=True,
        blank=True,
        help_text="登录用户姓名",
    )
    username = models.CharField(
        max_length=32,
        verbose_name="登录用户名",
        null=True,
        blank=True,
        help_text="登录用户名",
    )
    ip = models.CharField(
        max_length=32,
        verbose_name="登录ip",
        null=True,
        blank=True,
        help_text="登录ip",
    )
    agent = models.TextField(
        verbose_name="agent信息",
        null=True,
        blank=True,
        help_text="agent信息",
    )
    browser = models.CharField(
        max_length=200,
        verbose_name="浏览器名",
        null=True,
        blank=True,
        help_text="浏览器名",
    )
    os = models.CharField(
        max_length=200,
        verbose_name="操作系统",
        null=True,
        blank=True,
        help_text="操作系统",
    )
    continent = models.CharField(
        max_length=50,
        verbose_name="州",
        null=True,
        blank=True,
        help_text="州",
    )
    country = models.CharField(
        max_length=50,
        verbose_name="国家",
        null=True,
        blank=True,
        help_text="国家",
    )
    province = models.CharField(
        max_length=50,
        verbose_name="省份",
        null=True,
        blank=True,
        help_text="省份",
    )
    city = models.CharField(
        max_length=50,
        verbose_name="城市",
        null=True,
        blank=True,
        help_text="城市",
    )
    district = models.CharField(
        max_length=50,
        verbose_name="县区",
        null=True,
        blank=True,
        help_text="县区",
    )
    isp = models.CharField(
        max_length=50,
        verbose_name="运营商",
        null=True,
        blank=True,
        help_text="运营商",
    )
    area_code = models.CharField(
        max_length=50,
        verbose_name="区域代码",
        null=True,
        blank=True,
        help_text="区域代码",
    )
    country_english = models.CharField(
        max_length=50,
        verbose_name="英文全称",
        null=True,
        blank=True,
        help_text="英文全称",
    )
    country_code = models.CharField(
        max_length=50,
        verbose_name="简称",
        null=True,
        blank=True,
        help_text="简称",
    )
    longitude = models.CharField(
        max_length=50,
        verbose_name="经度",
        null=True,
        blank=True,
        help_text="经度",
    )
    latitude = models.CharField(
        max_length=50,
        verbose_name="纬度",
        null=True,
        blank=True,
        help_text="纬度",
    )
    login_type = models.IntegerField(
        default=1,
        choices=LOGIN_TYPE_CHOICES,
        verbose_name="登录类型",
        help_text="登录类型",
    )

    class Meta:
        db_table = "login_log"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_time",)
