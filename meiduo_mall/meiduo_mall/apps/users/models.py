from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# 自定义用户模型类 ，继承自AbstarctUser，并且可以追加字段
class User(AbstractUser):
    """用户模型类"""
    # 1.追加手机号字段
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name