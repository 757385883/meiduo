"""

使用JWT，默认的返回值仅有token，
我们还需在返回值中增加username和user_id。

所以在源代码中 重写可以修改返回值的 函数，
在utils文件重写，并且要配置一下，让JWT知道重写了某个函数

通过修改该视图的返回值可以完成我们的需求。
"""
import re

from django.contrib.auth.backends import ModelBackend

from meiduo_mall.meiduo_mall.apps.users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    根据account 查询用户
    :param account: 可以是用户名或者手机号
    :return: user 或者 None
    # 封装对象，这样根据用户名查询的用户对象
    在别的地方使用时，可以直接调用

    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)

        else:
            user = User.objects.get(username=account)

    except User.DoseNotExist:
        return None
    else:
        return  user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重点问题：怎么解决又可以用户名登录，又可以手机号登录？
        1.修改JWT后端认证系统中负责校验用户名的类中函数
        2.在这个函数中就是不仅仅可以通过用户名来查询数据库中，是否有该用户
        也可以使用 手机号查询
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        """

        # 查询user对象
        user = get_user_by_account(username)

        #校验user 是否存在已经密码是否正确
        if user and user.check_password(password):
            return user