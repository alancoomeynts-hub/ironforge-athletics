from django.urls import path

from . import views

app_name = "membership"

urlpatterns = [
    path("join/", views.membership_types, name="join"),
    path("manage/", views.manage_membership, name="manage"),
]
