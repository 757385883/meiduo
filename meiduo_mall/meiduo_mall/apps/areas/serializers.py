from rest_framework import serializers
from .models import Area
class AreaSerializer(serializers.ModelSerializer):
    """定义省级数据的序列化器；只做序列化
    list 行为使用
    """
    class Meta:
        model = Area
        fields = ['id','name']


class SubsAreasSerializer(serializers.ModelSerializer):
    """定义城市市区数据；只做序列化
        retrieve 行为 返回单一结果
    """
    # 关联AreaSerializer这个序列器
    # 无论从多方获取一方的数据还是从一方获取多方的数据
    # 都是使用 关联字段 subs获取
    # subs 里面的数据，来源于关联的序列化器序列化之后的结果，就按照这个序列化器返回list的形式，返回subs的数据
    subs = AreaSerializer(many=True,read_only=True)
    class Meta:
        model = Area
        fields = ['id','name','subs']
