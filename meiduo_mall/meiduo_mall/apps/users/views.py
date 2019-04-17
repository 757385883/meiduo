from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from . import serializer
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