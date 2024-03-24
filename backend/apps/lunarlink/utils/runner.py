# -*- coding: utf-8 -*-
"""
@File    : runner.py
@Time    : 2023/1/16 15:24
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 在线调试Python代码
"""

import shutil
import sys
import os
import subprocess
import tempfile

from lunarlink.utils import loader
from backend.settings import BASE_DIR

EXEC = sys.executable

if "uwsgi" in EXEC:
    # 修复虚拟环境下，用uwsgi执行时，PYTHONPATH还是用系统默认的
    EXEC = EXEC.replace("uwsgi", "python")


class DebugCode:
    """调试Python代码"""

    def __init__(self, code):
        self.__code = code
        self.resp = None
        self.temp = tempfile.mkdtemp(prefix="LunarLink")

    def run(self):
        """
        dumps debugtalk.py and run
        :return:
        """
        try:
            os.chdir(self.temp)
            file_path = os.path.join(self.temp, "debugtalk.py")
            # 将code写入debugtalk.py
            loader.FileLoader.dump_python_file(file_path, self.__code)
            # 修复驱动代码运行时，找不到配置httprunner包
            run_path = [BASE_DIR]
            run_path.extend(sys.path)
            env = {"PYTHONPATH": ":".join(run_path)}
            self.resp = decode(
                subprocess.check_output(
                    [EXEC, file_path], stderr=subprocess.STDOUT, timeout=60, env=env
                )
            )
        except subprocess.CalledProcessError as e:
            self.resp = decode(e.output)
        except subprocess.TimeoutExpired:
            self.resp = "RunnerTimeOut"
        os.chdir(BASE_DIR)
        shutil.rmtree(self.temp)


def decode(s: bytes) -> str:
    """
    将字节串转换成字符串
    :return:
    """
    try:
        return s.decode("utf-8")
    except UnicodeDecodeError:
        return s.decode("gbk")
