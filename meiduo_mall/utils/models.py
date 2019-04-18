# 新建基类模型
from django.db import models
"""
BaseModel主要用于继承，因为大部分模型类都有创建时间和更新时间这两个字段，
继承后，不用重复书写这两个字段
"""

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表