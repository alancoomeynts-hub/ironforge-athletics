from django.urls import path
from . import views

app_name = "community"
urlpatterns = [
    path(
        "",
        views.render_community_board,
        name="community",
    ),
    path(
        "post/<int:pk>/<slug:slug>",
        views.post_detail,
        name="post",
    ),
    path(
        "post/create/",
        views.create_post,
        name="create_post",
    ),
]
