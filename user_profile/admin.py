from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','member_since','date_of_birth')
    list_filter = ('user','member_since')
    search_fields = ('user__username','first_name','last_name')
    raw_id_fields = ('user',)