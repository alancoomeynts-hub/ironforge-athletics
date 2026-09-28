from .models import MembershipType
from django.shortcuts import render

def membership_types(request):
    types= MembershipType.objects.filter(is_available=True)
    return render(request, "membership/join.html", {"membership_types": types})