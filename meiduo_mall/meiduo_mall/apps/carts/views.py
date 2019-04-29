from django_redis import get_redis_connection
from rest_framework.views import APIView
from . import serializers
from rest_framework.response import Response
from rest_framework import status

import pickle
import base64
class CartView(APIView):

    """操作购物⻋：增删改查
    用户登录和未登录 都可以访问该接口的前提：
    1.必传 jwt token，因为如果不传无法识别用户信息
    2.不能指定权限，保证未登录用户可以访问

    必传 jwt token ，不能指定权限
    """

    def perform_authentication(self, request):
        """重写执行认证方法perform_authentication的目的：
        是为了保证用户在登录或者未登录状态都可以访问该视图，
        可以避免用户未登录，但是传入了 JET token时，在认证过程中报401错误"""
        pass

    def post(self, request):
        """添加购物⻋"""
        # 创建序列化器，校验参数，并返回校验之后的参数
        #序列化器中需要传入需要检验的参数，这是post请求，参数在请求体重，
        # 所以data要从request.data 中获取 d ata=request.data
        serializer = serializers.CartSerializer(data=request.data)
        # 调用序列化器中的方法，校验参数，
        # 允许自定义抛出错误信息，raise_exception= True
        serializer.is_valid(raise_exception= True)

        # 取出校验后的参数
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selcted')

        # 判断用户是否登录
        try: # 尝试从请求中获取用户信息，不存在 则为none
            user = request.user
        except Exception:
            user = None

        # 用户是登录的状态
        if user is not None and user.is_authenticated:
            #如果是以登录用户，存储购物车到redis
            # 创建链接到redis的对象
            redis_conn = get_redis_connection('cart')
            # 创建管道对象
            pl = redis_conn.pipeline()

            # 将sku_Id 和count 存入hash
            # hash 是redis中的一种数据形式
            # hash = {key：         'cart_%s' % user.id  key为键 ，field为域，value 是值
            # {
            #     field ：value      sku_id：count
            # }}
            # hincrby :自动实现自增量，会自动判断sku_Id，是否已经存在，如果存在就向原有的count值累加；不存在，就是count值

            # redis_conn.hincrby('cart_%s' % user.id ,sku_id,count)
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 将sku_id 写入到set 中 ，有去重功能 ，就是被勾选的sku_id放入set中
            pl.sadd('selected_%s' %user.id,sku_id)

            # 执行pl ,进行存储
            pl.execute()
           # 相应 序列化之后的而结果
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        eles:
            # 如果是未登录用户，存储购物车到cookie
            # 读取出cookie中原有的购物车数据,从cookie中获取的就是字符串
            cookie_cart_str=request.COOKIES.get('cart')

            # 判断cookie中的购物车数据是否存在，如果存在再转字典；反之，给空字典
            if cookie_cart_str:
                cookie_cart_bytes =cookie_cart_str.encode()
                cookie_cart_bytes_dict=base64.b64decode(cookie_cart_bytes)
                cookie_cart_dict=pickle.loads(cookie_cart_bytes_dict)
            else:
                # 返回空字典，是为了方便下面要使用，将购物车的数据存入字典
                cookie_cart_dict = {}
            # 判断sku_id 是否已经存在cookie_cart_dict中，存在则累加count中的值，不存在即保存新值
            if sku_id in cookie_cart_dict:
                old_count = cookie_cart_dict[sku_id]['count']
                count += old_count
            # 无论sku_id 是否已经存在都需要走这一步，所以构造新字典时，存入全新的值
            cookie_cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }
            # 将新的字典转成经过编码的字符串
            new_cookie_cart_bytes_dict = pickle.dumps(cookie_cart_dict)

            cookie_cart_str_bytes = base64.b64encode(new_cookie_cart_bytes_dict)

            cookie_cart_str_new = cookie_cart_str_bytes.decode()
            # 构造响应对象
            response = Response(serializer.data,status=status.HTTP_201_CREATED)
            # 将新购物车字符串，写入到cookie，
            # 并将cookie携带到响应对象中

            response.set_cookie('cart',)
            # 响应

    def get(self, request):
        """读取购物⻋"""
        # 判断用户是否登录
        try:  # 尝试从请求中获取用户信息，不存在 则为none
            user = request.user
        except Exception:
            user = None

        # 用户是登录的状态
        if user is not None and user.is_authenticated:
            # 如果是以登录用户，存储购物车到redis
            # 创建链接到redis的对象
            redis_conn = get_redis_connection('cart')
            # 查询hash 里面的所有sku_id 和count
            # 使用 hgetall方法 ，根据建查询所有的域和值
            #查询出来 byte类型的字典
            #{
            #     b'sku_id':b'count_1'
            #     b'sku_id_2':b'count_2'
            # }

            redis_cart_dict =redis_conn.hgetall('cart_%s' %user.id)

            # 查询set 中的sku_Id
            redis_selected_set =redis_conn.smembers('selected_%s' % user.id)
        else:
            # 如果是未登录用户，存储购物车到cookie
            # 读取出cookie中原有的购物车数据,从cookie中获取的就是字符串
            cookie_cart_str = request.COOKIES.get('cart')

            # 判断cookie中的购物车数据是否存在，如果存在再转字典；反之，给空字典
            if cookie_cart_str:
                cookie_cart_bytes = cookie_cart_str.encode()
                cookie_cart_bytes_dict = base64.b64decode(cookie_cart_bytes)
                cookie_cart_dict = pickle.loads(cookie_cart_bytes_dict)
            else:
                # 返回空字典，是为了方便下面要使用，将购物车的数据存入字典
                cookie_cart_dict = {}
    pass

    def put(self, request):
        """修改购物⻋"""

    pass

    def delete(self, request):
        """删除购物⻋"""

    pass