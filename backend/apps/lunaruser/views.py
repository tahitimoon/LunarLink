from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema


from backend.utils.request_util import save_login_log
from lunarlink.models import LoginLog
from lunaruser.common import response
from lunaruser import serializers
from lunarlink.utils.decorator import request_log


User = get_user_model()


class LoginView(APIView):
    """
    登录视图，用户名与密码匹配返回token
    """

    authentication_classes = ()
    permission_classes = ()

    @swagger_auto_schema(request_body=serializers.UserLoginSerializer)
    def post(self, request):
        """
        用户名密码一致返回token
        {
            username: str
            password: str
        }
        """
        try:
            username = request.data["username"]
            password = request.data["password"]
        except KeyError:
            return Response(response.KEY_MISS)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(response.LOGIN_FAILED)

        # 0后面还需要优化定义明确
        if user.is_active == 0:
            return Response(response.USER_BLOCKED)

        # JWT token creation
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response.LOGIN_SUCCESS.update(
            {
                "id": user.id,
                "user": user.username,
                "name": user.name,
                "is_superuser": user.is_superuser,
                "show_hosts": user.show_hosts,
                "token": token,
            }
        )
        request.user = user
        save_login_log(request=request)
        return Response(response.LOGIN_SUCCESS)


class UserView(APIView):
    def get(self, request):
        users = User.objects.filter(is_active=1)
        ser = serializers.UserModelSerializer(instance=users, many=True)
        return Response(ser.data)


class LoginLogView(GenericViewSet):
    """
    登录日志接口
    list:查询
    """

    queryset = LoginLog.objects.all()
    serializer_class = serializers.LoginLogSerializer

    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        search = request.query_params.get("search")
        queryset = self.get_queryset().order_by("-create_time")
        if search:
            queryset = queryset.filter(
                Q(ip__contains=search) | Q(name__contains=search)
            )

        pagination_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagination_queryset, many=True)

        return self.get_paginated_response(serializer.data)
