import base64
import pickle
from django_redis import get_redis_connection

def merge_cart_cookie_to_redis(request, user, response):
    """合并cookies购物车到redis购物车中"""

    # 读取cookie 中的购物车数据
    cookie_cart_str = request.COOKIES.get('cart')

    # 判断cookie中的购物车数据是否存在，如果存在再转字典；反之，z直接返回，不用进行合并
    if not cookie_cart_str:
        return None
    cookie_cart_bytes = cookie_cart_str.encode()
    cookie_cart_bytes_dict = base64.b64decode(cookie_cart_bytes)
    cookie_cart_dict = pickle.loads(cookie_cart_bytes_dict)

    # 读取redis中的购物车数据
    redis_conn = get_redis_connection('cart')
    #读取hash中的sku_Id和count
    redis_cart_dict = redis_conn.hgetall('cart_%S' % user.id )

    # 读取set中的sku_id
    redis_cart_selected = redis_conn.smembers('selected_%s' %user.id)

    # 遍历cookie中的购物车数据，合并到redis
    # 首先准备一个新的中间字典：
    # 为了手机redis中原有的数据，也为了保证在合并的redis购物车数据的类型和cookie中的一样


    new_redis_cart_dict = {}

    for sku_id,count in redis_cart_dict.items():
        new_redis_cart_dict[int(sku_id)]= int(count)

    # 遍历cookie购物车
    # 先合并hash中的数据
    for sku_id, cookie_cart in cookie_cart_dict.items():
        new_redis_cart_dict[sku_id] = cookie_cart['count']

        # 在判断是否勾选，合并到set中
        if cookie_cart['seleted']:
            # redis_cart_selected:集合对象，add（）方法是直接向集合中最佳元素。类似于列表的insert（）
            redis_cart_selected.add(sku_id)

    # 将new_redis_cart_dict和redis_cart_selected同步到redis中的购物车
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' %user.id ,new_redis_cart_dict)
    pl.sadd('selected_%s' %user.id,*redis_cart_selected)
    pl.execute()

    #   清空cookie中的购物车
    response.delete_cookie('cart')

    # 一定要将response返回到视图中，在视图中才能将response对象交给用户
    return response