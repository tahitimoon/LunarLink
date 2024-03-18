from django.contrib import admin
from django.contrib.auth import get_user_model

from lunarlink.models import Project

# Register your models here.

Users = get_user_model()


class ProjectAdmin(admin.ModelAdmin):
    # 列表要显示的字段
    list_display = (
        "name",
        "responsible",
        "get_groups",
        "get_creator_name",
        "get_updater_name",
        "create_time",
        "update_time",
    )

    def get_creator_name(self, obj):
        """返回项目创建者的名字"""
        return obj.creator.name if obj.creator else "-"

    def get_updater_name(self, obj):
        """返回项目创建者的名字"""
        user = Users.objects.filter(id=obj.updater).first()
        return user.name if user else "-"

    get_creator_name.short_description = "创建人"
    get_updater_name.short_description = "更新人"

    def get_groups(self, obj):
        """返回项目所属的所有分组"""
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups.short_description = "所属分组"

    def has_add_permission(self, request):
        return False  # 移除增加按钮

    def has_delete_permission(self, request, obj=None):
        return False  # 移除删除按钮

    # 指定在编辑页面上要显示的字段
    fields = [
        "name",
        "desc",
        "responsible",
        "yapi_base_url",
        "yapi_openapi_token",
        "jira_project_key",
        "jira_bearer_token",
        "groups",
    ]

    # 指定不可编辑的字段
    readonly_fields = ("responsible",)

    # 为ManyToMany字段提供一个水平滚动选择器
    filter_horizontal = ("groups",)

    def get_queryset(self, request):
        # 获取原始的queryset
        qs = super().get_queryset(request)

        # 如果是超级管理员，返回所有项目
        if request.user.is_superuser:
            return qs

        # 获取当前用户所在的所有分组
        user_groups = request.user.groups.all()

        # 基于分组来过滤项目
        return qs.filter(groups__in=user_groups).distinct()


admin.site.register(Project, ProjectAdmin)
