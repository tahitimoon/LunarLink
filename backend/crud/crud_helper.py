# -*- coding: utf-8 -*-
"""
@File    : crud_helper.py
@Time    : 2023/1/14 16:23
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : -
"""

import traceback
from typing import Dict, Tuple, TypeVar

from loguru import logger

from lunarlink.models import BaseTable

BModel = TypeVar("BModel", bound=BaseTable)


def create(creator: str, model: BModel, payload: Dict) -> None:
    try:
        logger.info(f"input: create={model.__name__}, payload={payload}")
        obj = model.objects.create(creator=creator, **payload)
    except Exception as e:
        logger.warning(traceback.format_exc())
        raise e
    logger.info(f"create {model.__name__} success, id: {obj.id}")


def get_or_create(
    model: BModel,
    filter_kwargs: Dict,
    defaults: Dict,
) -> Tuple[BaseTable, bool]:
    """

    :param model:
    :param filter_kwargs:
    :param defaults:
    :return:
    """
    logger.info(
        f"input get_or_create={model.__name__}, "
        f"filter_kwargs={filter_kwargs}, "
        f"defaults={defaults}"
    )
    obj, created = model.objects.get_or_create(
        defaults=defaults,
        **filter_kwargs,
    )

    return obj, created


def update(obj: BModel, updater: str, payload: Dict) -> BaseTable:
    logger.info(
        f"input: update model={obj.__class__.__name__}, id={obj.id}, payload={payload}"
    )
    if updater:
        obj.updater = updater
    for attr, value in payload.items():
        if hasattr(obj, attr) is False:
            logger.warning(f"{attr=} not in obj fields, it will not update")
        setattr(obj, attr, value)
    try:
        obj.save()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise e
    logger.info(f"update {obj.__class__.__name__} success, id: {obj.id}")
    return obj
