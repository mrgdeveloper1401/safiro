from django.urls import path

from .views import ProfileView, DriverView

app_name = "temp_auth_app"

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('driver/', DriverView.as_view(), name='driver'),
]
