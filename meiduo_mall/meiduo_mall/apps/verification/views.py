# Create your views here.
# 定义图片验证码类视图 ,第一步
import random

from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.celery_tasks.sms.tasks import send_sms_code
from . import serializer

from meiduo_mall.meiduo_mall.libs.yuntongxun.sms import CCP
from .import constants
from meiduo_mall.meiduo_mall.apps.verification.captcha import captcha
# 选择apiview的原因是，类视图并没有使用到序列化器
# 但是 因为需要校验参数，所以继承GenericAPIView，在反序列化阶段有字段的校验功能
class SMSCodeView(GenericAPIView):

    # 指定序列化器
    serializer_class = serializer.ImageCodeCheckSerializer


    def get(self,request,mobile):
        # 接受参数：mobile，image_code_id，text
        # 校验参数：image_code_id，text
        #对比text和服务器的图片验证码内容

        # 创建序列化对象
        # d反序列化传入的参数data=，获取查询字符串request.query_params
        serializer = self.get_serializer(data=request.query_params)
        # 校验参数 raise_exception=True 可以在全局自定义抛出异常的格式
        # is_valid 开始校验参数
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code ='%06d' %random.randint(0,999999)
        #发送短信验证码,使用第三方插件发送短信验证码
        # 此处是耗时操作 ，可能因为三方软件或者网络问题阻塞程序的进行
        # 要解决这个问题，使用celery异步服务器
        # CCP().send_template_sms(sms_code,[constants.IMAGE_CODE_REDIS_EXPIRES//60],1)

        # 异步发送短信验证码
        # delay : 将延时任务，添加到异步任务队列，并处罚异步任务，让worker可以观察到
        send_sms_code.delay(mobile,sms_code)



        # #存储短信验证码
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' % mobile,constants.IMAGE_CODE_REDIS_EXPIRES,sms_code)
        #
        # # 存储是否60s重复发送短信的标记，解决恶意刷新，阻止不断发送短信
        # # 在序列化器serializer 中进行比较，标记存在则不能发送
        # redis_conn.setex('sms_flag_%s' % mobile,constants.SMS_FLAG_TIME,1)

        # 使用管道pipeline ，让redis的多个指令，能回链接redis一次就执行完成多个指令
        # 解决多次链接redis数据库的问题,优化
    #PL 是管道对象，直接使用pl进行redis的存储
        pl = redis_conn.pipeline()

        pl.setex('sms_%s' % mobile,constants.IMAGE_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('sms_flag_%s' % mobile,constants.SMS_FLAG_TIME,1)
        # 最后要记得执行execute()
        pl.execute()
        #相应发送结果
        return Response({'message':111})
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