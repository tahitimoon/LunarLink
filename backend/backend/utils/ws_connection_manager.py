# -*- coding: utf-8 -*-
"""
@File    : ws_connection_manager.py
@Time    : 2023/9/12 17:09
@Author  : geekbing
@LastEditTime : -
@LastEditors : -
@Description : -
"""
import asyncio
import logging
import json
from typing import TypeVar

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

MsgType = TypeVar("MsgType", str, dict, bytes)


class ConnectionManager(AsyncWebsocketConsumer):
    active_connections = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None  # 初始化 user_id 属性

    async def connect(self):
        self.user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        exist = self.active_connections.get(self.user_id)
        if exist:
            await self.close()
        else:
            self.active_connections[self.user_id] = self
            logger.debug(f"websocket: 用户[{self.user_id}]建立连接成功！")
        await self.accept()
        # asyncio.create_task(self.send_heartbeat())

    async def disconnect(self, close_code):
        if self.user_id is not None:
            del self.active_connections[self.user_id]
            logger.debug(f"websocket: 用户[{self.user_id}] 已安全断开！")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message_type = data.get("type")
            if message_type in self.questions_and_answers_map:
                response = self.questions_and_answers_map[message_type].format(
                    user_id=self.user_id
                )  # 格式化字符串以包含 user_id
                await self.send_personal_message(
                    self.user_id, response
                )  # 使用 self.user_id
            else:
                # 添加其他消息类型的处理逻辑
                pass
        elif bytes_data:
            # 在这里添加你的二进制数据处理逻辑
            pass

    @staticmethod
    async def pusher(connection: AsyncWebsocketConsumer, message: MsgType) -> None:
        if isinstance(message, str):
            await connection.send(text_data=message)
        elif isinstance(message, dict):
            await connection.send(text_data=json.dumps(message))
        elif isinstance(message, bytes):
            await connection.send(bytes_data=message)
        else:
            raise TypeError(f"websocket不能发送{type(message)}的内容！")

    @classmethod
    async def send_personal_message(cls, user_id: int, message: MsgType) -> None:
        """
        发送个人信息
        """
        connection = cls.active_connections.get(user_id)
        if connection:
            await cls.pusher(connection, message)

    @classmethod
    async def send_data(cls, user_id, msg_type, record_msg):
        msg = dict(type=msg_type, record_msg=record_msg)
        await cls.send_personal_message(user_id, msg)

    questions_and_answers_map = {
        "HELLO SERVER": "Hello {user_id}",
        "HEARTBEAT": "{user_id}",
    }

    async def send_heartbeat(self):
        while True:
            await self.send_personal_message(self.user_id, {"type": 3})
            await asyncio.sleep(60)


# ws_manage = ConnectionManager()
