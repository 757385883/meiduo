from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Area
from . import serializers




class AreasViewsSet(ReadOnlyModelViewSet):
    """使用视图集 ：省市区视图集
    重点提示，为设么要使用视图集？
    第一视图包含两种查询情况，第二：两种查询都是对一张表的查询


    1.查询省数据时，返回所有省市list，所以是返回省级列表行为
    2.retrieve 返回单一数据 ：返回城市和区县
    """
    # 禁用分页效果
    pagination_class = None

    # 指定查询集，重写
    # 查询集也要根据行为返回不同的数据
    # queryset= Area.objects.all()
    def get_queryset(self):
        if self.action == 'list':
            # 返回 父类字段为空的所有省级数据，all（），filter（）都可以返回查询集
            return Area.objects.filter(parent=None)
        else:
            # 把所有的都返回，让他自己找
            return Area.objects.all()

    # 怎样从多个序列化器指定相应行为的序列化器？
    # 重写获取序列化器get_serializer_class(self):方法，
    # 根据相应的行为选择相应序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            #返回list行为对应的序列化器
            return serializers.AreaSerializer
        else:
            return serializers.SubsAreasSerializer
