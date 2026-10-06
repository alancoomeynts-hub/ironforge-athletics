from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from community.models import Post
from .forms import UserEditForm, ProfileEditForm
from .models import Profile
from shop.models import Order
from membership.models import Membership


# Create your views here.
@login_required
def dashboard(request):
    user = request.user

    try:
        profile = request.user.profile

    except Profile.DoesNotExist:
        profile = None

    order_history = Order.objects.filter(user=user).order_by("-created_on")
    current_membership = (
        Membership.objects.filter(
            user=request.user,
            status__in=[
                Membership.Status.ACTIVE,
                Membership.Status.TRIALING,
                Membership.Status.PAST_DUE,
                Membership.Status.UNPAID,
                Membership.Status.PAUSED,
                Membership.Status.INCOMPLETE,
            ],
        )
        .select_related("membership_type")
        .first()
    )
    post_history = Post.objects.filter(author=user).order_by("-created_on")
    return render(
        request,
        "user_profile/dashboard.html",
        {
            "user": user,
            "profile": profile,
            "order_history": order_history,
            "current_membership": current_membership,
            "post_history": post_history,
        },
    )


@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("user_profile:dashboard")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)

    return render(
        request,
        "user_profile/edit_profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def member_profile(request, username):
    member = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=member, status=Post.Status.PUBLISHED).order_by(
        "-created_on"
    )

    return render(
        request,
        "user_profile/member_profile.html",
        {
            "member": member,
            "posts": posts,
        },
    )
