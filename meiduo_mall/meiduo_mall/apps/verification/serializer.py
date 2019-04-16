from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers
import logging

# 日志记录器
logger = logging.getLogger('django')

# 校验图片验证码的序列化器
class ImageCodeCheckSerializer(serializers.Serializer):

    #定义检验字段：定义的校验字段要么和模型类的属性一样，要么和参数的key一样
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4,max_length=4)

    # 定义校验的函数
    def validate(self, attrs):
        """
        对text 和 image_code_id联合检验
        :param attrs: validated_data 是已经在字段交验过的数据
        :return: 如果校验成功，返回attrs ；反之，抛出异常

        """
        #读取attrs 中的数据
        image_code_id =attrs.get('image_code_id')
        text = attrs.get('text')
        # 获取连接到redis的对象
        redis_conn =get_redis_connection('img_%s' % image_code_id)
        # 获取redis中的存储的图片验证码内容
        image_code = redis_conn.get('img_%s'% image_code_id)
        if image_code is None:
            raise serializers.ValidationError('无效验证码')

        # 删除图片验证码,防止暴力测试，：必须先拿到图片验证码的内容，再删除
        # 这是个附带的业务逻辑可有可无
        # 因为链接redis 可能会有报错，这样会阻塞主程序的继续执行，
        #所以只是try ，然后把信息记录到日志，不能抛出异常
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)


        # py3 中的redis 存储的数据，读取出来都是bytes类型
        #想要比较 ，要先把image_code 从字节转成字符串,解码decode
        image_code = image_code.decode()
        # 对比参数text和redis中的图片验证码内容
        # text.lower() 忽略大小写
        if text.lower() != image_code.lower():
            raise serializers.ValidationError('图片验证码输入错误')


        # 判断用户是否使用一个手机号在60秒内，重复获取验证码
        #就是判断redis中的短信标记是否存在
        # 怎样从视图中获取 mobile这个参数，
        # 视图通过获取查询字符串得到mobile参数，存储在kwargs属性中
        #序列化器得到视图的参数
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('sms_flag_%s' %mobile)
        if send_flag:
            raise serializers.ValidationError('频繁发送短信')

        return attrs