from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from . import serializer
class VerifyEmailView(APIView):
    """验证邮箱的本质就是，查询用户，把用户的email_active字段修改为ture

    目的：1.用户点击激活连接后，发送请求；
        2.从链接中查询字符串读取token，并解密读取user_id；
        3.然后根据user_id查询当前要认证的用户，将用户的email_active设置为Ture

    """
    def get(self,request):
        # 获取token
        # request.query_params.get从查询字符串中获取参数
        token = request.query_params.get('token')
        if token is None:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        #因为 在这个视图中并没有传入实力对象，所以check_verify_email_token这个方法，无法通过实例直接调用
        #所以把这个方法写成静态方法@staticmethod，可以直接使用类调用

        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)

        # 将用户的email_active = Ture
        user.email_active = True
        user.save()

        return Response({'msg': "ok"})







# 添加邮箱
class EmailView(UpdateAPIView):
    """
    UpdateAPIView 用于修改数据的视图的父类，含有put方法
    """
    #def put(self): # 以为要修改数据，所以是put请求

    # 同样需要制定权限
    permission_classes = [IsAuthenticated]

    # 指定序列化器
    serializer_class = serializer.Emailserializer
class UserView(CreateAPIView):
    """
    用户注册
    1.为什么使用CreateAPIView？
    首先需要存储用户数据，所以是需要使用到反序列化器
    其次：CreateAPIView已经写过post方法，含有create（）和save（）
    我们只需要指定序列化器，同事在序列化器中校验字段的数据
    """
    serializer_class = serializer.CreateUserSerializer

# 判断用户名是否已存在
class UserView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count':count
        }

        return Response(data)

# 判断手机号是否已存在
class MobileCountView(APIView):
    # 读取手机号数量
    def get(self,request,mobile):
        count = User.objects,filter(mobi =mobile)>count()

        data ={
            'mobile':mobile
            ,'count':count
        }
        return Response(data)

class UserDetaView(RetrieveAPIView):
    """
    一.为什么使用RetrieveAPIView作为父类？
        1.他可以实现查询后的序列化
        2.响应单一结果就使用RetrieveAPIView，就是本视图的登录用户
        3.get 方法已经定义好，只需要指定序列化器
        4.def get(self,request):
        #得到当前用户的信息
        #创建序列化器
        #进行序列化
        #将序列化结果返回
        pass

    二、必须用户登陆后才能访问此接口
        1.所以要指定权限
        2.因为源代码中 调用self.get_object()方法获取单一数据对象时，必须依赖于主键，也就是user_id
        ，但是源代码中无法传入id ，只能重写该返方法
        """
    #指定权限:必须是登录用户才能访问该接口
    # permission_classes = 权限的指定
    # IsAuthenticated 登录用户权限
    permission_classes = [IsAuthenticated]

    # 指定序列化器
    serializer_class = serializer.UserDetaSerializer

    # 重写 get_object() 方法

    def get_object(self):
        # 在这个方法返回中返回当前的登录用户信息
        # 因为用户发送请求，在请求对象中已经包含用户的信息
        return self.request.user