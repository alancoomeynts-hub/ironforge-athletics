from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

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
        raise PermissionDenied

    return wrapper
