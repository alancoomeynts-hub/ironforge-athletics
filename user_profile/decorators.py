from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from membership.models import Membership


def staff_or_membership_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *arg, **kwargs):
        is_active_member = Membership.objects.filter(
            user=request.user, status=Membership.Status.ACTIVE
        ).exists()
        if is_active_member or request.user.is_staff:
            return view(request, *arg, **kwargs)
        messages.warning(
            request,
            "Choose a membership plan to join the conversation.",
        )
        return redirect(reverse("membership:join"))

    return wrapper
