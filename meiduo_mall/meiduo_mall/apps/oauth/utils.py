from urllib.parse import urlencode

from meiduo_mall.meiduo_mall import settings


class QAuthQQ:
    """qq登录的工具类：封装了请求登录的部分功能"""

    def __init__(self,client_id=None,client_secret=None,redirect_uri=None,state=None,):
        """1.构造方法，用户初始化QAuthQQ对象，并传入一些实力函数常用的参数
        2.绑定对象传入参数，self.client_id = client_id
        参数会存储在堆区，对象消失，参数才会没有
        如果是函数局部的定义的变量，存储在栈区，函数执行后，在栈区的内存就直接销毁，
        因此变量也随之销毁
        """
        # 参数可传可不传，在配置文件中settings配置默认参数，
        # 如果有参数会读取参数，如果没有，会读取or 后面的默认值
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET

        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state =state   or settings.QQ_STATE # 用于保存登录成功后的跳转页面

        # QQ_CLIENT_ID = '101474184'
        # QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
        # QQ_STATE = '/'
    def get_login_url(self):
        # 获取login_url 并返回
        # 1.准备QQ服务器的url
        login_url ="https://graph.qq.com/oauth2.0/show?"

        # 准备参数
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',



        }
        # 将字典转成查询字符串格式 from urllib.parse import urlencode
        query_params = urlencode(params)
        # 4.拼接login_url
        login_url += query_params
        # 5.返回
        return login_url
# 新建基类模型
from django.db import models
"""
BaseModel主要用于继承，因为大部分模型类都有创建时间和更新时间这两个字段，
继承后，不用重复书写这两个字段
"""

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表