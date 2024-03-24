# -*- coding: utf-8 -*-
"""
@File    : auth.py
@Time    : 2023/1/13 15:06
@Author  : Jiang Bing
@LastEditTime : -
@LastEditors : -
@Description : 登录认证
"""

import jwt
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.authentication import jwt_get_username_from_payload
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class MyJWTAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise, returns `None`.
        """
        jwt_value = request.META.get("HTTP_AUTHORIZATION", None)
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = "签名过期"
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = "签名解析失败"
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return user, jwt_value

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _("Invalid payload.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = "用户不存在"
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = "用户已禁用"
            raise exceptions.AuthenticationFailed(msg)

        return user
