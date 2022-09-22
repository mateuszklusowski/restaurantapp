from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


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
