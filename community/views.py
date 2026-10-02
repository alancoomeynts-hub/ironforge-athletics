from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.utils.text import slugify
from community.models import Post, PostImage, Comment
from .forms import PostForm, CommentForm


def render_community_board(request):
    """Render community board with new post form and paginator"""
    published_posts = Post.objects.filter(status="published").order_by("-created_on")
    form = PostForm()
    paginator = Paginator(published_posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "community/community.html",
        {
            "published_posts": page_obj,
            "form": form,
        },
    )


def post_detail(request, pk, slug):
    post = get_object_or_404(
        Post,
        pk=pk,
        slug=slug,
    )
    comment_form = CommentForm()
    comments = post.comments.all()

    return render(
        request,
        "community/post.html",
        {
            "post": post,
            "comment_form": comment_form,
            "comments": comments,
        },
    )


@login_required
def create_post(request):
    status = None
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            action = request.POST.get("action")
            if action == "draft":
                status = Post.Status.DRAFT
            elif action == "publish":
                status = Post.Status.PUBLISHED

            post.status = status
            post.author = request.user
            post.slug = slugify(post.title) or "post"
            post.save()

            for photo in request.FILES.getlist("photos"):
                PostImage.objects.create(
                    post=post,
                    image=photo,
                )

            messages.success(
                request,
                "Post created successfully!",
            )

            return redirect(reverse("community:community"))

    form = PostForm()
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_on")
    return render(
        request,
        "community/community.html",
        {
            "form": form,
            "posts": posts,
        },
    )


def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("community:post", pk=post.pk, slug=post.slug)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            form.save()

            for photo in request.FILES.getlist("photos"):
                PostImage.objects.create(
                    post=post,
                    image=photo,
                )
            messages.success(request, "Post updated successfully!")
            if request.POST.get("origin")=="dashboard":
                return redirect("user_profile:dashboard")

    return redirect("community:post", pk=post.pk, slug=post.slug)


def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("community:post", pk=post.pk, slug=post.slug)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        if request.POST.get("origin") == "dashboard":
            return redirect("user_profile:dashboard")
    return redirect("community:community")


def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect("community:post", pk=post.pk, slug=post.slug)


def edit_comment(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)

    if comment.author != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("community:post", pk=comment.post.pk, slug=comment.post.slug)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully!")
    return redirect("community:post", pk=comment.post.pk, slug=comment.post.slug)


def delete_comment(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)

    if comment.author != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("community:post", pk=comment.post.pk, slug=comment.post.slug)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
    return redirect("community:post", pk=comment.post.pk, slug=comment.post.slug)
