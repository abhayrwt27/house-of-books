from django.urls import path
from . import views

urlpatterns = [
    path("auth/", views.auth_view, name="auth"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
]



