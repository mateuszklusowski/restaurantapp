from django.urls import path

from . import views as api_views

app_name = 'user'

urlpatterns = [
    path('create/', api_views.CreateUserView.as_view(), name='create-user'),
    path('me/', api_views.UserDetailView.as_view(), name='user-detail'),
    path('password-change',
         api_views.UserPasswordChangeView.as_view(),
         name='password-change'),
    path('reset-password/',
         api_views.PasswordResetRequestView.as_view(), name='reset-password'),
    path('reset-password/<uidb64>/<token>/',
         api_views.PasswordResetConfirmView.as_view(),
         name='reset-password-confirm'),
]
