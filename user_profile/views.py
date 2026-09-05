from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserEditForm, ProfileEditForm
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

@login_required
def edit_profile(request):
    user=request.user
    profile=user.profile
    if request.method == 'POST':
        user_form=UserEditForm(request.POST, instance=request.user)
        profile_form=ProfileEditForm(request.POST,instance=request.user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form=UserEditForm(instance=request.user)
        profile_form=ProfileEditForm(instance=profile)

    return render(request,"user_profile/edit_profile.html",{'user_form':user_form,'profile_form':profile_form})