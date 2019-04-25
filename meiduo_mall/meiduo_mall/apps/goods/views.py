from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from .models import SKU
from . import serializers
class SKUListView(ListAPIView):
    """
    商品显示列表，ListAPIView 序列化返回列表数据
    """
    # 指定查询集
    queryset = SKU.objects.all()


    # 指定序列化器
    serializer_class = serializers.SKUSerializer

    # 指定排序的后端,排序后端OrderingFilter，自己完成排序效果，
    # 并自动返回 以下这些字段
    # count	int	是	数据总数
    # next	url	是	下一页的链接地址
    # previous	url	是	上一页的链接地址
    # results	sku[]	是	商品sku数据列表
    filter_backends = [OrderingFilter]

    # 指定排序字段: 字段名必须和模型的属性同名，不需要在这里指定是否倒叙，只指定哪些需要排序的字段即可
    ordering_fields = ('create_time','price','sales')

    # 因为返回的查询集是根据 商品id 查询后的列表，而不是所有商品信息
    # 所以重写 获取查询集方法
    def get_queryset(self):
        """
        /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
        1.怎样获取视图路径中传入的 category_id参数？
           该参数已经被视图获取，在def get(self, request, *args, **kwargs):
           方法获取到kwargs 中，所以使用 视图对象.kwargs.get()来获取该参数
        """

        category_id =self.kwargs.get('category_id')

        # 根据category_id ，查询SKU，is_launched是商品是否下架字段
        return SKU.objexts.filter(category_id=category_id,is_launched = True)
