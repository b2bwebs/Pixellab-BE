from rest_framework import serializers
from clients.models import Client
from custom_users.models import User
from oauth2_provider.models import Application
from oauth2_provider.generators import generate_client_secret, generate_client_id
from clients.models import AllowedOrigin
from constants import (
    CLIENT,
)


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    # email unique validation pending,email pending
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=False)
    allowed_origins = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Client
        fields = [
            "email",
            "password",
            "company_name",
            "contact_no",
            "gst_no",
            "sec_mobile",
            "address",
            "allowed_origins",
            "rate_limit",
        ]

    def validate_email(self, value):
        # Check if we are in the update operation
        if self.instance:
            # Skip validation if the email hasn't changed
            if self.instance.user.email == value:
                return value
            # Skip validation if email belongs to the current user
            if (
                User.objects.filter(email=value)
                .exclude(pk=self.instance.user.pk)
                .exists()
            ):
                raise serializers.ValidationError("Email address must be unique.")
        else:
            # Perform normal uniqueness validation for create operation
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email address must be unique.")
        return value

    def create(self, validated_data):
        # Extract email and password from validated data
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        allowed_domains = validated_data.pop("allowed_origins", [])

        # Create a new user
        user = User.objects.create_user(email=email, password=password, role=CLIENT)
        # Create OAuth2 application for the user
        client_id = generate_client_id()
        client_secret = generate_client_secret()
        # Get the current user from the request
        auth_user = self.context["request"].user
        application = Application.objects.create(
            user=user,
            name=f"{user.email}'s Application",
            client_id=client_id,
            client_secret=client_secret,
            client_type=Application.CLIENT_CONFIDENTIAL,
            # authorization_grant_type=Application.GRANT_PASSWORD,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        )
        # Assign the user to the client data
        validated_data["user"] = user
        validated_data["current_client_id"] = client_id
        validated_data["current_client_secret"] = client_secret
        # Set created_by and updated_by to the current user
        validated_data["created_by"] = auth_user
        validated_data["updated_by"] = auth_user
        validated_data["is_allow_all_origin"] = "*" in allowed_domains
        # Create a new client
        client = Client.objects.create(**validated_data)

        # later use
        # Save allowed origins
        if not validated_data["is_allow_all_origin"]:
            for domain in allowed_domains:
                AllowedOrigin.objects.create(client=client, origin=domain)
        return client

    def update(self, instance, validated_data):
        email = validated_data.pop("email")
        # Get the current user from the request
        auth_user = self.context["request"].user
        if email:
            if User.objects.exclude(pk=instance.user.pk).filter(email=email).exists():
                raise serializers.ValidationError("Emeail address must be unique.")
            instance.user.email = email
            instance.user.save()
        # allowed_domains = validated_data.pop("allowed_origins", [])
        instance.company_name = validated_data.get(
            "company_name", instance.company_name
        )
        instance.address = validated_data.get("address", instance.address)
        instance.rate_limit = validated_data.get("rate_limit", instance.rate_limit)
        instance.contact_no = validated_data.get("contact_no", instance.contact_no)
        instance.gst_no = validated_data.get("gst_no", instance.gst_no)
        instance.sec_mobile = validated_data.get("sec_mobile", instance.sec_mobile)
        instance.updated_by = auth_user
        instance.save()

        return instance


class RelatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "id", "unique_id"]  # Include all fields from the User model


class AllowedOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedOrigin
        fields = ["origin", "id"]


class ClientRetrieveSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer()
    allowed_origins = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "address",
            "allowed_origins",
            "user",
            "rate_limit",
            "is_allow_all_origin",
            "contact_no",
            "gst_no",
            "sec_mobile",
        ]

    def get_allowed_origins(self, instance):
        active_origins = instance.allowed_origins.filter(is_active=True)
        serializer = AllowedOriginSerializer(instance=active_origins, many=True)
        return serializer.data


class ClientListSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer()  # Nested representation of the User object
    allowed_origins = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "user",
            "company_name",
            "address",
            "current_client_id",
            "current_client_secret",
            "is_active",
            "rate_limit",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "allowed_origins",
            "contact_no",
            "gst_no",
            "sec_mobile",
        ]

    def get_allowed_origins(self, instance):
        active_origins = instance.allowed_origins.filter(is_active=True)
        serializer = AllowedOriginSerializer(instance=active_origins, many=True)
        return serializer.data


class ClientSelfRetrieveSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer()
    allowed_origins = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "address",
            "allowed_origins",
            "user",
            "current_client_id",
            "current_client_secret",
            "rate_limit",
        ]

    def get_allowed_origins(self, instance):
        active_origins = instance.allowed_origins.filter(is_active=True)
        serializer = AllowedOriginSerializer(instance=active_origins, many=True)
        return serializer.data
