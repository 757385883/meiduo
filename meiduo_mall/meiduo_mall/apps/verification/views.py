from django.shortcuts import render

# Create your views here.
# 定义图片验证码类视图 ,第一步
from rest_framework.views import APIView


class ImageCodeView(APIView):

    def get(self,request,image_code_id):
        """提供图片验证码"""
        pass