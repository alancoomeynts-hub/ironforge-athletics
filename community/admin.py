from django.contrib import admin

from .models import Comment, Post, PostImage


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = [
        "content",
        "created_on",
        "author",
    ]


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    readonly_fields = ["image", "caption"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "status"]
    list_filter = ["status", "created_on", "author"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    ordering = ["-created_on", "status"]
    inlines = [CommentInline, PostImageInline]
    show_facets = admin.ShowFacets.ALWAYS
