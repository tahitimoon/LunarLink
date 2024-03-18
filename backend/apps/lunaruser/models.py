from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class MyUser(AbstractUser):
    """
    使用AbstractUser可以对User进行扩展使用，添加用户自定义的属性
    """

    phone = models.CharField(
        verbose_name="手机号码",
        unique=True,
        null=True,
        max_length=11,
        help_text="手机号码",
    )
    show_hosts = models.BooleanField(
        verbose_name="是否显示Hosts相关的信息",
        default=False,
        help_text="是否显示Hosts相关的信息",
    )
    name = models.CharField(
        verbose_name="姓名",
        max_length=40,
        blank=True,
        null=True,
        help_text="姓名",
    )

    class Meta(AbstractUser.Meta):
        pass
