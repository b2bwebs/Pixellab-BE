from django.db import models
from django.conf import settings
from custom_users.models import BaseModel

User = settings.AUTH_USER_MODEL
# Create your models here.


class Client(BaseModel):
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        # You can set a related name for reverse lookup(ex:user.client_info)
        related_name="client_info",
        related_query_name="client",  # You can set a related query name for reverse lookup
        db_column="user_id",  # You can specify the name of the database column
    )
    company_name = models.CharField(max_length=100, blank=True, null=True)
    contact_no = models.CharField(max_length=100, blank=True, null=True)
    gst_no = models.CharField(max_length=100, blank=True, null=True)
    sec_mobile = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    current_client_id = models.CharField(max_length=100, blank=True, null=True)
    current_client_secret = models.CharField(max_length=250, blank=True, null=True)
    default_max_pages = models.PositiveIntegerField(default=4)

    rate_limit = models.IntegerField(default=1)
    is_allow_all_origin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"
        db_table = "clients"


class AllowedOrigin(BaseModel):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="allowed_origins"
    )
    origin = models.CharField(max_length=200)

    class Meta:
        db_table = "allowed_origins"
        verbose_name = "allowed origin"
        verbose_name_plural = "allowed origins"


class ClientAIParsingConfig(BaseModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.DO_NOTHING,
        related_name="ai_config",
        null=True,
        blank=True,
    )
    file_pages = models.PositiveIntegerField(default=1)
    max_final_pages = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.client} - Max Pages: {self.max_final_pages}"
