from django.urls import path,include 
from . import views
from rest_framework import routers  
# from rest_framework_jwt.views import obtain_jwt_token
# 路由器提供了一种自动确定 URL conf 的简便方法。
router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('group', views.GroupViewSet)
router.register('task', views.TaskViewSet)
router.register('profile', views.ProfileViewSet)
router.register('Participantship', views.ParticipantshipViewSet)
router.register('tag', views.TagViewSet)

# Create your views here.
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Questionnaire API')

# 使用自动 URL 路由连接我们的 API。
urlpatterns = [
    path('', schema_view),
    path('api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    # path('login/', obtain_jwt_token),
    path('register/', views.user_signup),
    path('login/', views.user_login),
    path('logout/', views.user_logout),
    path('avatar/',views.user_avatar),
    path('avatar/<image>',views.get_image),
    path('', include(router.urls)),
]