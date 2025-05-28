from rest_framework import serializers
from django.contrib.auth import authenticate
import logging
from django.core.cache import cache
from custom_users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

error_logger = logging.getLogger("error_logger")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "email", "password", "role")
        read_only_fields = (
            "id",
            "name",
        )
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "name": {"required": True},
        }


class AuthSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, max_length=128)

    def validate(self, attrs):
        user = None
        email = attrs["email"]
        password = attrs["password"]
        credentials = {
            "email": email,
            "password": password,
        }
        if not all(credentials.values()):
            message = "Must include Email and password"
            raise serializers.ValidationError(message)
        try:
            user = authenticate(**credentials)
        except Exception as e:
            error_logger.info(e)
        if not user:
            message = "Invalid Credentials"
            raise serializers.ValidationError(message)
        # if not user.is_login or user.is_deleted_user:
        #     message = 'You don\'t have permission to login, please contact admin'
        #     raise serializers.ValidationError(message)

        # token = UserJWTSerializer.get_token(user)
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)
        # access_token = token.access_token
        # cache.set(access_token["jti"], user.id, timeout=7776000)

        auth = {
            "refresh": str(refresh_token),
            "access": str(access_token),
        }
        user_data = UserDetailSerializer(user).data

        data = {"token": auth, "user": user_data}
        return data
