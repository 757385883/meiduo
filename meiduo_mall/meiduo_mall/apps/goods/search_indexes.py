from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text 用于接受用户输入的关键字
    # document ：指定文档，描述text字段，文档中
    #use_template： 在文档中使用模板语言，致命哪些字段可以传给text
    # 总结：text字段，属于复合字段，可以指定多个模型类的字段被他接收
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)