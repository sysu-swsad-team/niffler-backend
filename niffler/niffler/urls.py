"""niffler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from django.conf.urls import url
from questionnaire import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', admin.site.urls), # for swagger
    path('register/', views.Signup.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.user_logout),
    path('payment/',views.PaymentView.as_view()),
    path('payment/status/',views.PaymentStatusView.as_view()),
    path('avatar/<image>',views.GetImage.as_view()),
    path('avatar/',views.UserAvatar.as_view()),
    path('questionnaire/', include('questionnaire.urls')),
]

