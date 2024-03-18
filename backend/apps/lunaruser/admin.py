from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from lunarlink.models import Project

# Register your models here.
User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def accessible_projects(self, obj):
        user_groups = obj.groups.all()
        # 用多对多的关系来过滤出属于用户所在分组的项目。实际应用中可能会有更复杂的逻辑。
        return ", ".join(
            Project.objects.filter(groups__in=user_groups)
            .distinct()
            .values_list("name", flat=True)
        )

    accessible_projects.short_description = "可访问项目"

    list_display = (
        "username",
        "name",
        "is_active",
        "belong_groups",
        "accessible_projects",
    )

    # 编辑资料的时候显示的字段
    fieldsets = (
        (None, {"fields": ("username", "name", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    # 新增用户需要填写的字段
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "groups",
                ),
            },
        ),
    )
    filter_horizontal = ("groups",)

    def belong_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    belong_groups.short_description = "所属分组"
