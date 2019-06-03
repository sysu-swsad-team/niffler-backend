from django.urls import path,include 
from . import views
from rest_framework import routers

# 路由器提供了一种自动确定 URL conf 的简便方法。
router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('group', views.GroupViewSet)

# 使用自动 URL 路由连接我们的 API。
urlpatterns = [
    path('', include(router.urls)),
]
