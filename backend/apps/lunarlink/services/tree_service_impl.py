# -*- coding: utf-8 -*-
"""
@File    : tree_service_impl.py
@Time    : 2023/1/14 16:10
@Author  : geekbing
@LastEditTime : 2023/7/27 21:10
@LastEditors : geekbing
@Description : 树形结构操作
"""
from ast import literal_eval
import traceback
from typing import Dict, List, Optional

from loguru import logger

from crud.base_crud import GenericCURD
from lunarlink.dto.tree_dto import TreeOut, TreeUniqueIn, TreeUpdateIn
from lunarlink.models import API, Case, Relation
from lunarlink.utils.response import (
    TREE_GET_SUCCESS,
    TREE_UPDATE_SUCCESS,
    StandResponse,
)
from lunarlink.utils.tree import get_tree_max_id
from lunarlink.utils.enums.TreeTypeEnum import TreeType


class TreeService:
    def __init__(self):
        self.model = Relation
        self.curd = GenericCURD(self.model)

    def get_or_create(self, query: TreeUniqueIn) -> StandResponse[TreeOut]:
        default_tree = [
            {
                "id": 1,
                "label": "默认目录",
                "children": [],
            }
        ]
        tree_obj, is_created = self.curd.get_or_create(
            filter_kwargs=query.dict(),
            defaults={"tree": default_tree, "project_id": query.project_id},
        )
        if is_created:
            logger.info(f"tree created {query=}")
            body: List[Dict] = tree_obj.tree
        else:
            logger.info(f"tree exist {query}")
            body: List[Dict] = literal_eval(tree_obj.tree)

        node_api_case_counts = {}
        for node in body:
            if query.type == TreeType.API:
                TreeService.add_api_count_to_node(
                    tree_obj.project_id,
                    node,
                    node_api_case_counts,
                )
            else:
                TreeService.add_case_count_to_node(
                    tree_obj.project_id,
                    node,
                    node_api_case_counts,
                )

        for root_node in body:
            TreeService.add_api_case_count_to_tree(root_node, node_api_case_counts)

        tree = {
            "tree": body,
            "id": tree_obj.id,
            "success": True,
            "max": get_tree_max_id(body),
        }
        return StandResponse[TreeOut](**TREE_GET_SUCCESS, data=TreeOut(**tree))

    @staticmethod
    def add_case_count_to_node(project_id: int, node: Dict, node_case_count: Dict):
        """
        递归获取节点的用例数量
        :param project_id:
        :param node:
        :param node_case_count:
        :return:
        """
        node_id = node["id"]
        case_count = Case.objects.filter(
            project_id=project_id, relation=node_id
        ).count()
        node_case_count[node_id] = case_count

        for child in node.get("children", []):
            TreeService.add_case_count_to_node(project_id, child, node_case_count)

    @staticmethod
    def add_api_count_to_node(project_id: int, node: Dict, node_api_count: Dict):
        """
        递归获取节点的接口数量
        :param project_id:
        :param node:
        :param node_api_count:
        :return:
        """
        node_id = node["id"]
        api_count = API.objects.filter(project_id=project_id, relation=node_id).count()
        node_api_count[node_id] = api_count

        for child in node.get("children", []):
            TreeService.add_api_count_to_node(project_id, child, node_api_count)

    @staticmethod
    def add_api_case_count_to_tree(node: Dict, node_api_case_counts: Dict):
        """
        将节点的接口或用例数量嵌入原树形结构中
        :param node:
        :param node_api_case_counts:
        :return:
        """
        data_count = node_api_case_counts.get(node["id"], 0)
        if "children" in node:
            for child in node["children"]:
                data_count += TreeService.add_api_case_count_to_tree(
                    child, node_api_case_counts
                )
        node["data_count"] = data_count
        return data_count

    @staticmethod
    def check_related_api(node_id: int, project_id: int) -> bool:
        # 检查是否存在关联的接口
        return API.objects.filter(relation=node_id, project_id=project_id).exists()

    @staticmethod
    def check_related_case(node_id: int, project_id: int) -> bool:
        # 检查是否存在关联的用例
        return Case.objects.filter(relation=node_id, project_id=project_id).exists()

    def get_all_ids_from_tree(self, tree):
        """
        获取树的所有节点id
        :param tree:
        :return:
        """
        ids = [node["id"] for node in tree]
        for node in tree:
            if "children" in node:
                ids.extend(self.get_all_ids_from_tree(node["children"]))
        return ids

    def _check_related_api_recursive(self, current_tree, payload_tree, project_id):
        """
        提取payload.tree所有节点id，递归检查current_tree中是否存在这些id，如果不存在，检查是否有关联的API
        """
        payload_tree_id_list = self.get_all_ids_from_tree(payload_tree)

        for node in current_tree:
            if node["id"] not in payload_tree_id_list:
                # 这个节点正在被删除，检查是否有关联的API
                if self.check_related_api(node["id"], project_id):
                    return True

            # 如果该节点有子节点，继续递归检查
            if "children" in node and node["children"]:
                if self._check_related_api_recursive(
                    node["children"], payload_tree, project_id
                ):
                    return True
        return False

    def _check_related_case_recursive(self, current_tree, payload_tree, project_id):
        """
        提取payload.tree所有节点id，递归检查current_tree中是否存在这些id，如果不存在，检查是否有关联的用例
        """
        payload_tree_id_list = self.get_all_ids_from_tree(payload_tree)

        for node in current_tree:
            if node["id"] not in payload_tree_id_list:
                # 这个节点正在被删除，检查是否有关联的API
                if self.check_related_case(node["id"], project_id):
                    return True

            # 如果该节点有子节点，继续递归检查
            if "children" in node and node["children"]:
                if self._check_related_case_recursive(
                    node["children"], payload_tree, project_id
                ):
                    return True
        return False

    @staticmethod
    def get_current_tree(relation_obj) -> List:
        """
        获取当前的树形结构, 转成python对象
        :param relation_obj:
        :return:
        """
        if not relation_obj:
            return []
        return literal_eval(relation_obj.tree)

    def patch(self, tree_id: int, payload: TreeUpdateIn):
        """
        更新树形结构

        :param tree_id:
        :param payload:
        :return:
        """
        # 获取当前的树结构
        if not payload.tree:
            return StandResponse[Optional[TreeOut]](
                code="9999",
                success=False,
                msg="删除失败, 至少保留一个根目录",
                data=None,
            )
        relation_obj = self.curd.get_obj_by_pk(pk=tree_id)
        current_tree = self.get_current_tree(relation_obj)
        # 检查每个节点，如果在当前树中找到了这个节点，但在新树中找不到，就意味着这个节点被删除了
        if payload.type == TreeType.API:
            if self._check_related_api_recursive(
                current_tree, payload.tree, relation_obj.project_id
            ):
                # 如果存在关联的接口，返回提示信息
                return StandResponse[Optional[TreeOut]](
                    code="9999",
                    success=False,
                    msg="目录有关联接口，不能删除",
                    data=None,
                )
        elif payload.type == TreeType.CASE:
            # 如果存在关联的用例，返回提示信息
            if self._check_related_case_recursive(
                current_tree, payload.tree, relation_obj.project_id
            ):
                # 如果存在关联的接口，返回提示信息
                return StandResponse[Optional[TreeOut]](
                    code="9999",
                    success=False,
                    msg="目录有关联用例，不能删除",
                    data=None,
                )

        # 如果没有问题，尝试更新
        try:
            tree_obj = self.curd.update_obj_by_pk(
                pk=tree_id, updater="", payload=payload.dict()
            )
        except Exception as e:
            return self._handle_exception(e)

        tree: List[Dict] = tree_obj.tree
        node_api_case_counts = {}
        for node in tree:
            if payload.type == TreeType.API:
                TreeService.add_api_count_to_node(
                    tree_obj.project_id,
                    node,
                    node_api_case_counts,
                )
            else:
                TreeService.add_case_count_to_node(
                    tree_obj.project_id,
                    node,
                    node_api_case_counts,
                )

        for root_node in tree:
            TreeService.add_api_case_count_to_tree(root_node, node_api_case_counts)

        return StandResponse[TreeOut](
            **TREE_UPDATE_SUCCESS,
            data=TreeOut(tree=tree, id=tree_obj.id, max=get_tree_max_id(tree)),
        )

    @staticmethod
    def _handle_exception(e: Exception) -> StandResponse[Optional[TreeOut]]:
        err: str = traceback.format_exc()
        logger.warning(f"Exception {e} occurred with traceback: {err}")
        return StandResponse[Optional[TreeOut]](
            code="9999", success=False, msg=err, data=None
        )


tree_service = TreeService()
