from decimal import Decimal

from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from meiduo_mall.meiduo_mall.apps.goods.models import SKU
from meiduo_mall.meiduo_mall.apps.orders.models import OrderInfo, OrderGoods


class SaveOrderSerializer(serializers.ModelSerializer):
    """
    下单数据序列化器
    """
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self,validated_data):
        """ 重写序列化器的creat方法
        为了能够自己写代码按照需求保存订单基本信息和商品信息"""
        # 获取当前下单用户
        user = self.context['request'].user

        # 生成订单编号
        order_id = timezone.now().strftime()+('%09d' %user.id)

        address = validated_data.get('address')
        pay_method =validated_data.get('pay_method')

        # 保存订单基本信息数据 OrderInfo(主体业务逻辑1)
        # 模型类.object.creat（）：在创建模型类对象时，同时属性赋值，并同步到数据库
        order =    OrderInfo.objects.create(
            order_id= order_id,
            user =user,
            address =address,
            total_count =0,
            total_amount =  Decimal('0'),
            freight =Decimal('10.00'),
            pay_method = pay_method,
            # 状态，当if 条件成立时，执行前面，不成立执行后面，。
            #就是支付方式为支付宝，状态为待支付，否则为代发货。
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        )

        # 从redis中获取购物车结算商品数据
        redis_conn = get_redis_connection('cart')
        # 获取 hash中的sku_id和count
        cart_dict = redis_conn.hgetall('cart_%s' %user.id)
        redis_cart_selected = redis_conn.smembers('selected_%s' % user.id)

        #   读取出被勾选商品的信息
        cart = {}
        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(cart_dict[sku_id])
        # 读取出carts里面所有的sku_id
        sku_ids = cart.keys()
        #遍历 购物车中被勾选的商品信息
        for sku_id in sku_ids:
            sku = SKU.objects.get(id = sku_id)


        # 判断商品库存是否充足
        cart_sku_count = cart[sku_id]
        if cart_sku_count > sku.stock:
            raise serializers.ValidationError('库存不足')

        # 减少商品库存，增加商品销量
        sku.stock -= cart_sku_count
        sku.sales += cart_sku_count
        sku.save()
        # 修改SPU 销量
        sku.goods.sales += cart_sku_count
        sku.goods.save()#  同步到数据库

        # 保存订单商品数据
        OrderGoods.objects.create(
            order=order,
            sku=sku,
            count=cart_sku_count,
            price=sku.price,
        )

        # 在redis购物车中删除已计算商品数据
        order.total_count += order.freight
        order.save()


        # 返回新建的资源对象
        return order


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)