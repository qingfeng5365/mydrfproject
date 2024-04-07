from django.db import models


# Create your models here.
class Admin(models.Model):
    """管理员表"""
    username = models.CharField(verbose_name="账号", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
