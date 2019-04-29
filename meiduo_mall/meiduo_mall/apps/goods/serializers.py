from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers
from .models import SKU
from .search_indexes import SKUIndex





class SKUSerializer(serializers.ModelSerializer)
    """ 序列化输出商品SKU信息"""
    class Meta:
        model = SKU
        # 输出 ：序列化的字段
        fields=('id','name','price','default_image_url','comments')

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    # object 是嵌套字段，object中的数据以上面定义的SKUSerializer序列化器返回相应字段的数据
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
