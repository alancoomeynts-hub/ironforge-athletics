from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','member_since','date_of_birth')
    list_filter = ('user','member_since')
    search_fields = ('user__username','user__first_name','user__last_name','default_phone_number','user__email')
    raw_id_fields = ('user',)