# -*- coding: utf-8 -*-
"""
@File    : permissions.py
@Time    : 2023/8/23 14:46
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : 自定义权限类
"""
from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAdminUser
from lunarlink import models


# class HasProjectAccess(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # 检查请求的对象是否属于用户的组
#         return obj.groups.filter(id__in=request.user.groups.all()).exists()


class HasProjectAccess(BasePermission):
    message = "您没有执行此操作的权限"

    def has_permission(self, request, view):
        # 如果用户是超级管理员，允许访问所有项目
        if request.user.is_superuser:
            return True

        # 获取当前用户所在的所有分组
        user_groups = request.user.groups.all()

        # 获取请求参数中的项目ID
        project_id = view.kwargs.get("pk") or request.query_params.get("project")

        # 如果项目ID存在，检查项目是否属于用户的分组
        if project_id:
            return models.Project.objects.filter(
                pk=project_id, groups__in=user_groups
            ).exists()

        # 如果没有项目ID且视图方法是 'list' 或 'create'，则不需要进一步检查，因为 get_queryset 已经做了筛选
        if view.action in ["list", "add"]:
            return True

        # 对于其他方法，可能需要检查对象级的权限
        return False


class IsCreatorOrReadOnly(BasePermission):
    """
    自定义权限，确保只有对象的创建者才可以修改或删除对象。
    """

    def has_object_permission(self, request, view, obj):
        # 对于GET、HEAD或OPTIONS请求，任何请求都允许读取权限，因此我们始终允许这些请求。
        if request.method in permissions.SAFE_METHODS:
            return True

        # 判断请求的用户是否是对象的创建者。
        return obj.creator == request.user


class CustomIsAdminUser(IsAdminUser):
    message = "您没有执行此操作的权限"
