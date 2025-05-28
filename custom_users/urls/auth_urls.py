from django.urls import path
from custom_users.views import (
    LoginView,
    LogoutAPIView,
)
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path("login/", LoginView.as_view(), name="login-view"),
    path("logout/", LogoutAPIView.as_view(), name="logout-view"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
