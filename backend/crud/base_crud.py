# -*- coding: utf-8 -*-
"""
@File    : base_curd.py
@Time    : 2023/1/14 16:22
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from rest_framework.generics import get_object_or_404

from crud import crud_helper


class BaseCURD(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def create_obj(self, creator: str, payload: Any) -> None:
        ...

    @abstractmethod
    def get_obj_by_pk(self, pk: int):
        ...

    @abstractmethod
    def get_obj_by_unique_key(self, unique_key: Dict):
        ...

    @abstractmethod
    def get_or_create(self, filter_kwargs: Dict, defaults: Dict):
        ...

    @abstractmethod
    def list_obj(self, page_filter: Dict) -> List[Dict]:
        ...

    @abstractmethod
    def update_obj_by_pk(self, pk: int, updater: str, payload: Dict):
        ...

    @abstractmethod
    def delete_obj_by_pk(self, pk: int) -> bool:
        ...


class GenericCURD(BaseCURD):
    def delete_obj_by_pk(self, pk: int) -> bool:
        self.get_obj_by_pk(pk=pk).delete()
        return True

    def update_obj_by_pk(self, pk: int, updater: str, payload: Dict):
        return crud_helper.update(
            obj=self.get_obj_by_pk(pk=pk), updater=updater, payload=payload
        )

    def list_obj(self, page_filter: Dict) -> List[Dict]:
        return self.model.objects.filter(**page_filter)

    def get_or_create(self, filter_kwargs: Dict, defaults: Dict):
        return crud_helper.get_or_create(
            model=self.model, filter_kwargs=filter_kwargs, defaults=defaults
        )

    def get_obj_by_unique_key(self, unique_key: Dict):
        return get_object_or_404(self.model, **unique_key)

    def get_obj_by_pk(self, pk: int):
        return get_object_or_404(self.model, id=pk)

    def create_obj(self, creator: str, payload: Any) -> None:
        return crud_helper.create(creator=creator, model=self.model, payload=payload)
