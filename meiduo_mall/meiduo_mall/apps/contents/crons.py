# 这是将主页静态化
from collections import OrderedDict
from django.conf import settings
from django.template import loader
import os
import time
from goods.models import GoodsChannel
from .models import ContentCategory
def generate_static_index_html():
 """
 ⽣成静态的主⻚html⽂件
 """
print('%s: generate_static_index_html' % time.ctime())
 # 商品频道及分类菜单
 # 使⽤有序字典保存类别的顺序
 # categories = {
 # 1: { # 组1
 # 'channels': [{'id':, 'name':, 'url':},{}, {}...],
 # 'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]
 # },
 # 2: { # 组2
 #
 # }
 # }

 # 准备有序字典
 categories = OrderedDict()
 # 查询出所有的频道数据的分类数据，order_by 返回查询集，返回排序之后的查询集

channels = GoodsChannel.objects.order_by('group_id', 'sequence')
for channel in channels:
    group_id = channel.group_id # 当前组
    if group_id not in categories:
        categories[group_id] = {'channels': [], 'sub_cats': []}
 cat1 = channel.category # 当前频道的类别
 # 追加当前频道
 categories[group_id]['channels'].append({
 'id': cat1.id,
 'name': cat1.name,
 'url': channel.url
 })
 # 构建当前类别的⼦类别
 for cat2 in cat1.goodscategory_set.all():
    cat2.sub_cats = []
 for cat3 in cat2.goodscategory_set.all():
    cat2.sub_cats.append(cat3)
categories[group_id]['sub_cats'].append(cat2)
 # ⼴告内容
 contents = {}
 content_categories = ContentCategory.objects.all()
 for cat in content_categories:
    contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
 # 渲染模板
 context = {
 'categories': categories,
 'contents': contents
 }

 template = loader.get_template('index.html')
 html_text = template.render(context)
 # print(html_text)
 file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
 # encoding ： ⽤于解决在定时器执⾏时中⽂字符编码的问题
 with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html_text)