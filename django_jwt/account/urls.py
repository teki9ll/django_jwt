from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('refresh_access_token', CustomTokenRefreshView.as_view(), name="refresh_access_token"),
    path('', UserView.as_view(), name="user")
]