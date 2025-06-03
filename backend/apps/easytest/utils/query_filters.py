# -*- coding: utf-8 -*-
"""
@File    : filter_by_time_range.py
@Time    : 2023/12/25 09:49
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

from ast import literal_eval
from datetime import datetime, timedelta
from typing import Optional


from django.db.models import QuerySet

from apps.exceptions.error import RelationNotFound
from lunarlink.models import Relation
from lunarlink.utils.tree import find_all_children_ids


def filter_by_time_range(
    queryset: QuerySet,
    start_time: Optional[str],
    end_time: Optional[str],
) -> QuerySet:
    """
    根据提供的开始时间和结束时间过滤查询集

    :param queryset: 要过滤的原始查询集
    :param start_time: 过滤记录的开始时间（字符串格式，例如 'YYYY-MM-DD'）
    :param end_time: 过滤记录的结束时间（字符串格式，例如 'YYYY-MM-DD'
    :return QuerySet: 过滤后的查询集
    """
    if start_time and end_time:
        end_time = (
            datetime.strptime(end_time, "%Y-%m-%d")
            + timedelta(days=1)
            - timedelta(seconds=1)
        )
        return queryset.filter(create_time__range=[start_time, end_time])
    elif start_time:
        return queryset.filter(create_time__gte=start_time)
    elif end_time:
        end_time = (
            datetime.strptime(end_time, "%Y-%m-%d")
            + timedelta(days=1)
            - timedelta(seconds=1)
        )
        return queryset.filter(create_time__lte=end_time)
    return queryset


def filter_by_node(
    queryset: QuerySet,
    project: int,
    node: int,
    tree_type: int,
) -> QuerySet:
    """
    根据提供的节点过滤查询集

    :param queryset: 要过滤的原始查询集
    :param project: 项目id
    :param node: 目录id
    :param tree_type: 树的类型（例如 TreeType.CASE 或 TreeType.API）
    :return QuerySet: 更新后的查询集，根据指定的节点进行了过滤
    """
    if node is not None:
        try:
            tree_obj = Relation.objects.get(project=project, type=tree_type)
        except Relation.DoesNotExist:
            raise RelationNotFound("指定的目录不存在")

        tree = literal_eval(tree_obj.tree) if tree_obj else []
        node_ids = find_all_children_ids(tree, node)
        node_ids.append(node)
        return queryset.filter(relation__in=node_ids)

    return queryset
