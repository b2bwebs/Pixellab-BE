from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
import uuid


USER_ROLES = (
    (0, "SUPER ADMIN"),
    (1, "SUB ADMIN"),
    (2, "CLIENT"),
    (3, "TEST USER"),
    (4, "DATA ANALYST"),
    (5, "CLIENT SUB ADMIN"),
)


class CustomUserManager(BaseUserManager):
    """
    Custom user model where the email address is the unique identifier
    and has an role==0  field to allow access to the admin app
    """

    def create_user(self, email, password=None, role=3, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not password:
            raise ValueError("The password must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password, extra_fields):
        """
        Creates and saves a sub admin with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )

        user.role = 1
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", 0)
        if extra_fields.get("role") != 0:
            raise ValueError("Superuser must have role of Global Admin")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    unique_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="A unique identifier for the each object.",
    )

    role = models.PositiveSmallIntegerField(choices=USER_ROLES, blank=True, default=1)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="created_users",
        related_query_name="created_user",
        db_column="created_by",
    )
    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="updated_users",
        related_query_name="updated_user",
        db_column="updated_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = "users"

    def __str__(self):
        return self.email

    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission.
        """
        # Implement your logic here to check if the user has the specified permission.
        # For example:
        # return self.is_superuser  # Allow superusers to have all permissions
        return True  # Example: For now, return False by default

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app.
        """
        # Implement your logic here to check if the user has any permissions in the given app.
        # For example:
        # return self.is_superuser  # Allow superusers to have permissions in all apps
        return True  # Example: For now, return False by default

    @property
    def is_staff(self):
        """Users with role 0 (Super Admin) or 1 (Sub Admin) are considered staff."""
        return self.role in [0, 1]

    @property
    def is_admin(self):
        return self.role == 0


class BaseModel(models.Model):
    unique_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="A unique identifier for the each object.",
    )

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="%(class)s_created",
        related_query_name="%(class)s_created_by",
        db_column="created_by",
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="%(class)s_updated",
        related_query_name="%(class)s_updated_by",
        db_column="updated_by",
    )
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="%(class)s_deleted",
        related_query_name="%(class)s_deleted_by",
        db_column="deleted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserPermission(BaseModel):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    action = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )  # e.g., "approve_orders"
    is_allowed = models.BooleanField(default=False)  # True = Access granted
