# -*- coding: utf-8 -*-
"""
@File    : auxiliary_func.py
@Time    : 2022/12/6 15:56
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : -
"""
import base64
import os

from backend.settings import BASE_DIR


def img_value():
    """
    获取图片换算值
    :return:
    """
    file_path = os.path.join(BASE_DIR, "test_data/images/attachment.jpg")
    file_value = get_file_value(file_path)

    return file_value


def get_file_value(file_path):
    """
    解析编码文件，生成file参数的值
    :param file_path: 文件路径
    :return:
    """
    # 以二进制格式读取文件内容

    with open(file_path, "rb") as f:
        content = f.read()

    content = base64.b64encode(content)
    suffix_name = file_path.split(".")[-1]
    # file参数格式：文件名后缀 + @ + 文件内容进行base64编码后的字符串
    file_value = suffix_name + "@" + content.decode()

    return file_value
