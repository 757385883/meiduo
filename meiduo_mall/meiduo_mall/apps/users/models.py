from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from .  import constants
# Create your models here.
# 自定义用户模型类 ，继承自AbstarctUser，并且可以追加字段



class User(AbstractUser):
    """用户模型类"""
    # 1.追加手机号字段
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')

    # 追加邮箱是否激活字段
    email_active =models.BooleanField(default=False,verbose_name='邮箱验证状态')
    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    # 生成激活链接
    def generate_verify_email_url(self):
        # 创建加密对象，
        #settings.SECRET_KEY 是秘钥
        #VERIFY_EMAIL_TOKEN_EXPIRES 自定义的有效时间
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

        #创建被加密的字典
        data ={'user_id':self.id,'email':self.email}
        # 生成加密后的口令
        #serializer.dumps(data)生成bytes类型，decode解码成字符串
        token = serializer.dumps(data).decode()

        # 拼接 激活码
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url
    @staticmethod # 静态方法，类可以直接调用，实例对象也可调用
    def check_verify_email_token(token):
        """
        解码token
        读取出use_id ，查询当前认证用户
        :return:
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

        # 解码token ,要使用try
        try:

            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data.get('user_id')
            email = data.get('email')
            # 通过id查用户
            try:

                user   = User.objects.get(id=user_id,email=email)
            except User.DoseNotExist:
                return None
            else:
                return user