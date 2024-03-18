# -*- coding: utf-8 -*-
"""
@File    : tree.py
@Time    : 2023/1/14 16:46
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

import collections
from typing import Dict, List


# 默认分组id=1
label_id = 1


def get_tree_label(value, search_label):
    """
    根据分组名成查找分组id，默认为1
    :param value:
    :param search_label:
    :return:
    """
    global label_id
    if not value:
        return label_id

    if isinstance(value, list):
        for content in value:  # content -> dict
            if content["label"] == search_label:
                label_id = content[id]
            children = content.get("children")
            if children:
                get_tree_label(children, search_label)

    return label_id


def get_all_ycatid(value, list_id: List = None) -> List:
    """
    获取所有yapi的分组目录id
    :param value:
    :param list_id:
    :return:
    """
    if not value:
        return []  # the first node id

    if isinstance(value, list):
        for content in value:  # content -> dict
            yapi_catid = content.get("yapi_catid")
            if yapi_catid:
                list_id.append(yapi_catid)

            children = content.get("children")
            if children:
                get_all_ycatid(children)

    return list_id


def get_tree_ycatid_mapping(value, mapping: Dict = {}) -> Dict:
    """
    获取yapi分组id和faster api分组id的映射关系
    :param value:
    :param mapping: {"yapi_catid": "node_id"}
    :return:
    """
    if not value:
        return {}

    if isinstance(value, list):
        for content in value:  # content -> dict
            yapi_catid = content.get("yapi_catid")
            if yapi_catid:
                mapping.update({yapi_catid: content.get("id")})
            children = content.get("children")
            if children:
                get_tree_ycatid_mapping(children, mapping)

    return mapping


label = ""


def get_tree_relation_name(value, relation_id):
    """
    根据节点的id查找出节点的名字
    :param value:
    :param relation_id:
    :return:
    """
    global label
    if not value:
        return label

    if isinstance(value, list):
        for content in value:  # content -> dict
            if content["id"] == relation_id:
                label = content["label"]
            children = content.get("children")
            if children:
                get_tree_relation_name(children, relation_id)

    return label


def get_tree_max_id(tree: List) -> int:
    """
    广度优先遍历树，得到最大Tree max id
    :param tree:
    :return:
    """
    queue = collections.deque()
    queue.append(tree)
    max_id = 0
    while len(queue) != 0:
        sub_tree: List = queue.popleft()
        for node in sub_tree:
            children: List = node.get("children")
            max_id = max(max_id, node["id"])
            # 有子节点
            if len(children) > 0:
                queue.append(children)

    return max_id


def find_all_children_ids(tree: List, target_id: int) -> List:
    """
    从树形结构中查找目标节点的所有子节点 ID
    :param tree: 树形结构
    :param target_id: 目标节点 ID
    :return:
    """
    queue = tree.copy()
    while queue:
        node = queue.pop(0)
        if node["id"] == target_id:
            # 找到目标节点，开始收集其所有子节点的 ID
            child_ids = []
            children_queue = node.get("children", []).copy()
            while children_queue:
                child = children_queue.pop(0)
                child_ids.append(child["id"])
                children_queue.extend(child.get("children", []))
            return child_ids
        queue.extend(node.get("children", []))
    return []
