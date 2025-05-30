# Generated by Django 5.2.1 on 2025-05-29 06:01

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedOrigin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='A unique identifier for the each object.', unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('origin', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'allowed origin',
                'verbose_name_plural': 'allowed origins',
                'db_table': 'allowed_origins',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='A unique identifier for the each object.', unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=100, null=True)),
                ('gst_no', models.CharField(blank=True, max_length=100, null=True)),
                ('sec_mobile', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('current_client_id', models.CharField(blank=True, max_length=100, null=True)),
                ('current_client_secret', models.CharField(blank=True, max_length=250, null=True)),
                ('rate_limit', models.IntegerField(default=1)),
                ('is_allow_all_origin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'db_table': 'clients',
            },
        ),
    ]
