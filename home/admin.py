from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Gym,ContactSubmission

# Register your models here.

@admin.register(Gym)
class GymAdmin(SummernoteModelAdmin):
    summernote_fields = ('description','address','opening_hours')

admin.site.register(ContactSubmission)