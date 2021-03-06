import re
from rest_framework_jwt.settings import api_settings

from django_redis import get_redis_connection
from rest_framework import serializers
from .models import User
from meiduo_mall.celery_tasks.email.tasks import send_email
from . import models
class UserDetaSerializer(serializers.ModelSerializer):
    """用户的基本信息序列化器"""

    class Meta:
        model = User
        fields = ['id','username', 'mobile','email','email_active']

# 定义邮箱序列化器
class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # 指定需要接收和响应的所有字段
        fields= ['id','email']
        #因为email 字段在模型类定义时，可以为空，
        # 所以在序列化映射时，是非必传的，所以要重新指定email为必传
        extra_kwargs={
            # 指定email为必传字段
            'email':{
                'required': True
            }
        }

        def update(self,instance,validated_data):
            """
            重写序列化器的更新数据的方法
            1.用于指定的更新某些字段，因为put方法是全字段更新
            2.用于在此处发送邮件，在保存之后，响应之前
            :param instance: 外界传入的要更新的user对象
            :param validated_data: 已经校验后，准备更新某些字段的内容

            :return:返回修改后的user对象
            """
            # 修改email字段
            instance.email = validated_data.get('email')
            instance.save()

            # 生成激活链接,将生成链接的方法封装，写到用户模型类中，
            # 主要是方便获得用户的id,将此方法定义成实例方法，
            #可以直接用实力对象调用
            #instance 就是user对象
            verify_url = instance.generate_verify_email_url()

            # 触发发送邮件异步任务，在保存之后，响应之前
            # 必须调用delay，去触发异步任务
            send_email.delay(instance.email,'激活链接')

            return instance






# 创建用户注册的序列化器

class CreateUserSerializer(serializers.ModelSerializer):
    """
    serializers.ModelSerializer,因为要使用的序列化器中的模型类反序列化功能，
    所以使用serializers.ModelSerializer
    """


        # user模型类中没有的字段需要额外定义，否则序列化器无法映射到这些字段
    password2 = serializers.CharField(label='确认密码',write_only= True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)

    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段
    class Meta:
        moble = User # 序列化器映射user模型类的所有字段
        # 特地指定哪些字段需要序列化 id默认只读
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow','token')
        # 校验 用户名和密码
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True, # 只写
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
    # 然后依次对mobile，allow校验
    def validate_mobie(self, value):
        # 验证手机号
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        # 检验用户是否同意协议
        if value != 'ture':
            raise serializers.ValidationError('请用户同意协议')
        return value

    # 联合校验短信验证码和密码
        # attrs是请求的对象，里面含有字段数据的键值对
    def validate(self, data):
         # 判断两次密码是否一致
        if data['password'] != data['password2']:

            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码 'verify_codes' 是redis存储验证码的数据库名称
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']

        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    """
    重点注意：在将接受的所有参数存储到数据库中时，要记得先删除模型类没有的字段
    比如：User 模型类中就不包含 password2 ，sms_code，allow，
    所以要将这些字段先删除，需要重写 父类中的create方法，
    创建新的存储对象
    """
    def create(self, validated_data):
        #创建删除一些字段后的用户对象
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # 再调用父类create方法，创建用户对象
        user = super().create(validated_data)

        # 调用diango的认证系统加密
        user.set_password(validated_data['password'])
        # 提交用户对象到数据ku
        user.save()

        # 在保存数据之后，在返回结果之前
        # 设置JWT
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 将JWT生产的token 临时绑定到user对象上，一并相应给浏览器
        user.token =token
        # 因为user模型类并没有 token这个字段，所以需要额外添加到fields中
        #fields就是 输入，输出的所有字段，同时也要定义额外的字段token
        return user