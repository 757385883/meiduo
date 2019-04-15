from django.shortcuts import render

# Create your views here.
# 定义图片验证码类视图 ,第一步
from rest_framework.views import APIView


class ImageCodeView(APIView):

    def get(self,request,image_code_id):
        """提供图片验证码"""
        # 生成图片验证码的内容和图片

        # 将内容和uuid存储到redis

        #将图片相应给用户
