from django.db.models.fields import return_None
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Profile

# Create your views here.
@login_required
def dashboard(request):
    user = request.user
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile=None

    return render(
        request,
        'user_profile/dashboard.html',
        {
            'user': user,
            'profile': profile
        })

