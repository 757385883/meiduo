from django.shortcuts import render

# Create your views here.
# 定义QQ登录页面网址类视图
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import QAuthQQ

# url(r'^qq/user/$', views.QQAuthUserView.as_view()),
class QQAuthUserView(APIView):
  """⽤户扫码登录的回调处理"""
  def get(self, request):
      # 提取code请求参数
      # 使⽤code向QQ服务器请求access_token
      # 使⽤access_token向QQ服务器请求openid
      # 使⽤openid查询该QQ⽤户是否在美多商城中绑定过⽤户
      # 如果openid已绑定美多商城⽤户，直接⽣成JWT token，并返回
      # 如果openid没绑定美多商城⽤户，创建⽤户并绑定到openid

      pass
class QQAutURLView(APIView):
    """提供QQ登录页面网址视图
    重要提示：在视图中书写业务逻辑，而不书写怎样获得login_url的具体过程
    ，具体处理业务逻辑的过程在额外定义的工具类中去实现。
    这也是重要的面相对象开发的思想，而不是一步步把所有的过程都写在视图中的面相过程开发
    2.QAuthQQ()就是在.utils 中创建处理业务过程的工具类

    """
    def get(self,request):
        # 创建QAuthQQ对象
        oauth = QAuthQQ()

        # 获取qq 扫码登录页面网址
        login_url = oauth.get_login_url()

        # 响应login_url
        return Response({'login_url':login_url})