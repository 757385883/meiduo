from rest_framework import serializers

from meiduo_mall.meiduo_mall.apps.goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车序列化器：提供反序列化校验和序列化"""
    # 序列化需要校验和输出的字段
    sku_id = serializers.IntegerField(label='商品 SKU ID',min_value=1)
    count = serializers.IntegerField(label='商品数量',min_value=1)
    selected = serializers.BooleanField(label='是否勾选',default=True)

    # 对sku_Id 和count 联合校验
    def validate(self, attrs):
        # 读取sku_Id 和count
        sku_id = attrs.get('sku_id')
        count = attrs.get('count')

        # 校验sky_Id
        try:
            sku = SKU.objects.get(id = sku_id)
        except SKU.DoseNotExist:
            raise serializers.ValidationError('sku_id 不存在')

        #校验 count 要比库存小
        if count > sku.stock:
            raise serializers.ValidationError('库存不足')

        return attrs