from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from membership.models import Membership, MembershipType

# Register your models here.
admin.site.register(Membership)


@admin.register(MembershipType)
class MembershipTypeAdmin(SummernoteModelAdmin):
    summernote_fields = ("benefits",)
