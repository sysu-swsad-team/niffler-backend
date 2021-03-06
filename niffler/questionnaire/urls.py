from django.urls import path,include 
from . import views
from rest_framework import routers  
# from rest_framework_jwt.views import obtain_jwt_token
# 路由器提供了一种自动确定 URL conf 的简便方法。
router = routers.DefaultRouter()
# router.register('users', views.UserViewSet)
# router.register('group', views.GroupViewSet)
# router.register('task', views.TaskViewSet)
# router.register('profile', views.ProfileViewSet)
# router.register('Participantship', views.ParticipantshipViewSet)
# router.register('tag', views.TagViewSet)

# Create your views here.
# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_swagger_view(title='Questionnaire API')
from .swagger_schema import schema_view

# 使用自动 URL 路由连接我们的 API。
urlpatterns = [
    path('swagger/', schema_view),
    path('api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('profile/<pk>/', views.ProfileView.as_view({'get': 'retrieve'})),
    path('profile/', views.ProfileView.as_view({'get': 'get'})),
    path('profile/', views.ProfileView.as_view({'post': 'post'})),
    path('task/<pk>/', views.TaskView.as_view({'get': 'retrieve'})),
    path('task/', views.TaskView.as_view({
                                            'get': 'get',
                                            'post': 'create'
                                         })),
    path('task/cancel/<pk>/', views.TaskView.as_view({'post': 'cancel'})),
    path('task/claim/<pk>/', views.TaskView.as_view({'post': 'claim'})),
    path('participantship/cancel/<pk>/',
         views.ParticipantshipView.as_view({'post': 'cancel'})),
    path('participantship/confirm/<pk>/',
         views.ParticipantshipView.as_view({'post': 'confirm'})),
    path('participantship/comment/',
         views.ParticipantshipView.as_view({'post': 'comment'})),
    path('participantship/<pk>/', 
         views.ParticipantshipView.as_view({'get': 'retrieve'})),
    path('participantship/', views.ParticipantshipView.as_view(
                                                    {'post': 'create'})),
    path('tag/<pk>/', views.TagView.as_view({'get': 'retrieve'})),
    path('tag/', views.TagView.as_view({'get': 'get'})),
    path('', include(router.urls)),
]