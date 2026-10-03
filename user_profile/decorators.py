from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from membership.models import Membership
from functools import wraps


def staff_or_membership_required(view):
    @wraps(view)
    @login_required
    def wrapper(request,*arg,**kwargs):
        is_active_member = Membership.objects.filter(user=request.user, status=Membership.Status.ACTIVE).exists()
        if is_active_member or request.user.is_staff:
            return view(request,*arg,**kwargs)
        raise PermissionDenied
    return wrapper
