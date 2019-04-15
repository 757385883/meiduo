# Create your views here.
# 定义图片验证码类视图 ,第一步
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView

from .import constants
from meiduo_mall.meiduo_mall.apps.verification.captcha import captcha
# 选择apiview的原因是，类视图并没有使用到序列化器
class SMSCodeView(APIView):
    def get(self,request,mobile):
        # 接受参数：mobile，image_code_id，text
        # 校验参数：image_code_id，text
        #对比text和服务器的图片验证码内容

        # 生成短信验证码

        #发送短信验证码

        #存储短信验证码

        #相应发送结果

class ImageCodeView(APIView):

    def get(self,request,image_code_id):
        """提供图片验证码"""
        # 生成图片验证码的内容和图片
        text,image =captcha.generate_captcha()
        # 将内容和uuid存储到redis
        #得到redis数据库对象
        redis_conn=get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        #将图片相应给用户
        # return Response 默认相应json数据
        # return HttpResponse (相应内容，响应数据类型)
        return HttpResponse(image,content_type='image/jpg ')