from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 用户是否已存在 ,定义子路由
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),


    # JWT 实现登录认证功能，obtain_jwt_token就实现了登录的类视图功能
    url(r'^authorizations/$', obtain_jwt_token),


]