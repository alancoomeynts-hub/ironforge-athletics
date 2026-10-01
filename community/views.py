from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.utils.text import slugify
from community.models import Post, PostImage
from .forms import PostForm


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
    return render(
        request,
        "community/post.html",
        {
            "post": post,
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
                PostImage.objects.create(post=post, image=photo)
            return redirect(reverse("community:community"))

    form = PostForm()
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_on")
    return render(
        request,
        "community/community.html",
        {
            "form": form,
        },
    )
