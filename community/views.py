from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse,get_object_or_404
from django.utils.text import slugify
from community.models import Post, PostImage, Comment
from membership.models import Membership
from .forms import PostForm, CommentForm
from user_profile.decorators import staff_or_membership_required


@staff_or_membership_required
def render_community_board(request):
    """Display community board"""
    published_posts = Post.objects.filter(status="published").order_by("-created_on")
    form = PostForm()

    # Paginate the posts
    paginator = Paginator(published_posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Pass is_active_member or is_staff to the template context. Used to determine if user can create a new post
    is_active_member = Membership.objects.filter(
        user=request.user, status=Membership.Status.ACTIVE
    ).exists()
    can_access = is_active_member or request.user.is_staff

    return render(
        request,
        "community/community.html",
        {
            "published_posts": page_obj,
            "form": form,
            "can_access": can_access,
        },
    )


def post_detail(request, pk, slug):
    """Display a single post with comments and comment form."""
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


@staff_or_membership_required
def create_post(request):
    """Create a new post. Only staff and active members can create a new post."""
    status = None
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            # Determine the status based on the create post form action (draft or publish)
            action = request.POST.get("action")
            if action == "draft":
                status = Post.Status.DRAFT
            elif action == "publish":
                status = Post.Status.PUBLISHED

            post.status = status
            post.author = request.user
            post.slug = slugify(post.title) or "post"
            post.save()

            # Create post images for each photo in the form submission
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


@staff_or_membership_required
def edit_post(request, pk):
    """Edit a post. Only staff and author can edit a post."""
    post = get_object_or_404(Post, pk=pk)

    # Allow only staff and author to edit the post
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect(
            "community:post",
            pk=post.pk,
            slug=post.slug,
        )

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
            # if the user came from the dashboard, redirect them there
            if request.POST.get("origin") == "dashboard":
                return redirect("user_profile:dashboard")

    # Otherwise, redirect back to the post detail page
    return redirect(
        "community:post",
        pk=post.pk,
        slug=post.slug,
    )


@staff_or_membership_required
def delete_post(request, pk):
    """Delete a post. Only staff and author can delete a post."""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect(
            "community:post",
            pk=post.pk,
            slug=post.slug,
        )

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")

        if request.POST.get("origin") == "dashboard":
            return redirect("user_profile:dashboard")

    return redirect("community:community")


@staff_or_membership_required
def add_comment(request, pk):
    """Add a comment to a post."""
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

    return redirect(
        "community:post",
        pk=post.pk,
        slug=post.slug,
    )

@staff_or_membership_required
def edit_comment(request, pk):
    """Edit a comment. Only staff and author can edit a comment."""
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect(
            "community:post",
            pk=comment.post.pk,
            slug=comment.post.slug,
        )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully!")

    return redirect(
        "community:post",
        pk=comment.post.pk,
        slug=comment.post.slug,
    )

@staff_or_membership_required
def delete_comment(request, pk):
    """Delete a comment. Only staff and author can delete a comment."""
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect(
            "community:post",
            pk=comment.post.pk,
            slug=comment.post.slug,
        )

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully!")

    return redirect(
        "community:post",
        pk=comment.post.pk,
        slug=comment.post.slug,
    )
