

# 后端接口代码实现第二步,定义路由视图映射
from django.conf.urls import url
from . import views
urlpatterns = [
    # 图片验证码路由映射
    url(r'^/image_codes/(?P<image_code_id>[\w-]+)/$',views.ImageCodeView.as_view())
]