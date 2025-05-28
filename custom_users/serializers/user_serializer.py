from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from custom_users.models import UserPermission

User = get_user_model()


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = ["id", "action", "is_allowed"]


class UserSerializer(serializers.ModelSerializer):
    permissions = UserPermissionSerializer(
        many=True, required=False, source="userpermission_set"
    )
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "unique_id",
            "role",
            "is_active",
            "is_deleted",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "permissions",
            "password",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "unique_id"]

    def create(self, validated_data):
        """
        Create a new user instance, handling password and permissions correctly.
        """
        permissions_data = validated_data.pop("permissions", [])
        password = validated_data.pop("password", None)

        with transaction.atomic():  # Ensures atomicity
            user = super().create(validated_data)

            if password:
                user.set_password(password)
                user.save()

            # Bulk create permissions
            user_permissions = [
                UserPermission(user=user, **permission_data)
                for permission_data in permissions_data
            ]
            UserPermission.objects.bulk_create(user_permissions)

        return user

    def update(self, instance, validated_data):
        """
        Update a user instance, handling password and permissions efficiently.
        """
        permissions_data = validated_data.pop("permissions", [])
        password = validated_data.pop("password", None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if password:
                instance.set_password(password)
                instance.save()

            # Get existing permissions
            existing_permissions = {
                perm.action: perm for perm in instance.permissions.all()
            }

            new_permissions = set()
            for permission_data in permissions_data:
                action = permission_data["action"]
                new_permissions.add(action)

                if action in existing_permissions:
                    permission = existing_permissions[action]
                    if permission.is_allowed != permission_data.get(
                        "is_allowed", permission.is_allowed
                    ):
                        permission.is_allowed = permission_data.get(
                            "is_allowed", permission.is_allowed
                        )
                        permission.save()
                else:
                    UserPermission.objects.create(user=instance, **permission_data)

            # Remove old permissions that are no longer in the new data
            UserPermission.objects.filter(user=instance).exclude(
                action__in=new_permissions
            ).delete()

        return instance


class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "unique_id",
            "role",
            "is_active",
            "is_deleted",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "password",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "unique_id"]

    def create(self, validated_data):
        """
        Create a new user instance, handling password and permissions correctly.
        """
        password = validated_data.pop("password", None)

        with transaction.atomic():  # Ensures atomicity
            user = super().create(validated_data)

            if password:
                user.set_password(password)
                user.save()

        return user

    def update(self, instance, validated_data):
        """
        Update a user instance, handling password and permissions efficiently.
        """
        password = validated_data.pop("password", None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if password:
                instance.set_password(password)
                instance.save()

        return instance


class UserUpdateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "role",
            "is_active",
            "is_deleted",
            "updated_by",
            "password",
        ]

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop("permissions", [])
        password = validated_data.pop("password", None)

        with transaction.atomic():
            # Update core fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update password if provided
            if password:
                instance.set_password(password)
                instance.save()

        return instance
