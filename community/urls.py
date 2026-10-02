from django.urls import path
from . import views

app_name = "community"
urlpatterns = [
    path("", views.render_community_board, name="community"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:pk>/edit_post", views.edit_post, name="edit_post"),
    path("post/<int:pk>/delete_post", views.delete_post, name="delete_post"),
    path("post/<int:pk>/<slug:slug>", views.post_detail, name="post"),
    path("post/<int:pk>/add_comment/", views.add_comment, name="add_comment"),
    path("post/<int:pk>/edit_comment/", views.edit_comment, name="edit_comment"),
    path("post/<int:pk>/delete_comment/", views.delete_comment, name="delete_comment"),
]
