"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView

from core.views import health_check
from user.views import (BearerTokenFormView,
                        UserCreateFormView,
                        RefreshTokenFormView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/restaurants/', include('restaurant.urls')),
    path('api/user/', include('user.urls')),
    path('api/auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('api/health/', health_check, name='health-check'),
    path('api/orders/', include('orders.urls')),
    path('docs/',
         TemplateView.as_view(template_name='docs/redoc.html'),
         name='docs'),
    path('',
         TemplateView.as_view(template_name='main.html'),
         name='main-page'),
    path('generate-token/',
         BearerTokenFormView.as_view(),
         name='token-generate'),
    path('create-user/',
         UserCreateFormView.as_view(),
         name='create-user'),
    path('refresh-token/',
         RefreshTokenFormView.as_view(),
         name='token-refresh'),
    path('reset-password/',
         TemplateView.as_view(template_name='user/reset_password.html'),
         name='password-reset'),
]
