from django.urls import path
from . import views

app_name = "accounts"   # 🔴 ESTA LÍNEA ES CLAVE

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home, name="home"),
    path("welcome/", views.welcome_view, name="welcome"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
]
