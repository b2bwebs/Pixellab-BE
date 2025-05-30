from django.urls import path
from ocrapp.views import (
    upload_view,
)

urlpatterns = [
    path("upload", upload_view, name="upload-files"),
]
