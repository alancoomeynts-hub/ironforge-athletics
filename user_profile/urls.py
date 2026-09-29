from django.urls import path
from . import views

app_name = "user_profile"
urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
]
