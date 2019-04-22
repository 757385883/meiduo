# 指定视图集路由

from rest_framework.routers import DefaultRouter
from . import views
# 创建router对象
router = DefaultRouter()
# 生成符合restful风格的url
#r'areas' 绑定前缀，
router.register(r'areas', views.AreasViewsSet, base_name='areas')


urlpatterns = []

urlpatterns += router.urls