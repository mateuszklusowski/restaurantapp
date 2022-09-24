import os

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import Throttled

from .serializers import (UserSerializer,
                          UserPasswordChangeSerializer,
                          PasswordResetRequestSerializer)

from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model

from .forms import (BearerTokenForm,
                    UserCreateForm,
                    RefreshTokenForm)

from .tasks import generate_token


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        """Return authenticated user"""
        return self.request.user


class UserPasswordChangeView(generics.UpdateAPIView):
    serializer_class = UserPasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.set_password(request.data['new_password'])
            user.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not self.throttle_classes:
                self.throttle_classes.append(AnonRateThrottle)

            return Response(
                {'success': 'We have sent you an email with \
                 instructions for resetting your password.'},
                status=status.HTTP_200_OK
            )
        else:
            self.throttle_classes.clear()
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    def throttled(self, request, wait):
        raise Throttled(detail={
            "message": "You can reset your password only once a day."})


class PasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('main-page')
    success_message = 'Password changed successfuly'


class BearerTokenFormView(FormView):
    template_name = 'user/bearer_token.html'
    form_class = BearerTokenForm

    def form_valid(self, form):
        host = get_current_site(self.request).domain
        result = generate_token.delay(
            domain=host,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'])
        data = result.get()

        try:
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            return render(self.request,
                          'user/bearer_token.html',
                          {"access_token": access_token,
                           "refresh_token": refresh_token})
        except KeyError:
            return render(self.request,
                          'user/bearer_token.html',
                          {"key_error": data})


class UserCreateFormView(SuccessMessageMixin, FormView):
    template_name = 'user/create_user.html'
    form_class = UserCreateForm
    success_message = 'User created!'
    success_url = reverse_lazy('main-page')

    def form_valid(self, form):
        get_user_model().objects.create_user(**form.cleaned_data)
        return super().form_valid(form)


class RefreshTokenFormView(FormView):
    template_name = 'user/refresh_token.html'
    form_class = RefreshTokenForm

    def form_valid(self, form):
        host = get_current_site(self.request).domain
        result = generate_token.delay(
            domain=host,
            refresh_token=form.cleaned_data['refresh_token'],
            grant_type=os.environ.get('GRANT_TYPE2'))
        data = result.get()

        try:
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            return render(self.request,
                          'user/bearer_token.html',
                          {"access_token": access_token,
                           "refresh_token": refresh_token})
        except KeyError:
            return render(self.request,
                          'user/bearer_token.html',
                          {"key_error": data})
