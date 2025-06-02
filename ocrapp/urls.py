from django.urls import path
from ocrapp.views import (
    upload_view,
    response_list_view,
    mark_fetched_view,
)

urlpatterns = [
    path("upload", upload_view, name="upload-files"),
    path("response-list", response_list_view, name="response-list"),
    path("mark-fetched", mark_fetched_view, name="mark-fetched"),
]
