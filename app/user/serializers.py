from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .tasks import send_reset_password_email


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        min_length=5,
        required=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=5,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Check that old password is correct and different from new one"""
        user = self.context.get('request').user
        is_different = bool(data['new_password'] != data['old_password'])
        if not user.check_password(data['old_password']) or not is_different:
            msg = _('Old password is incorrect or similar to new one')
            raise serializers.ValidationError({'incorrect_password': msg})

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()

    class Meta:
        fields = '__all__'

    def validate_email(self, value):
        """Check that user exists"""

        if get_user_model().objects.filter(email=value).exists():
            user = get_user_model().objects.get(email=value)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(self.context.get('request')).domain
            relative_url = reverse('user:reset-password-confirm',
                                   kwargs={'uidb64': uidb64, 'token': token})
            absolute_url = 'http://{}{}'.format(current_site, relative_url)
            email_message = 'Here is your password reset link:\n{}\n\
                Link will exist for 1 hour. Hurry up!'.format(absolute_url)
            send_reset_password_email.delay(
                'Password reset link',
                email_message,
                user.email
            )

        else:
            msg = _('No user with this email address exists')
            raise serializers.ValidationError({'message': msg})

        return value
