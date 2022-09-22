from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import Throttled

from .serializers import (UserSerializer,
                          UserPasswordChangeSerializer,
                          PasswordResetRequestSerializer)

from django.contrib.auth.views import PasswordResetConfirmView


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


class PasswordResetConfirmView(PasswordResetConfirmView):
    pass
