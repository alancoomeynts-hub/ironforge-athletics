from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.models import User
from membership.models import Membership, MembershipType


@admin.register(Membership)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "membership_type",
        "status",
        "joined_date",
        "ended_at",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
        "status",
        "stripe_subscription_id",
    )

    readonly_fields = (
        "joined_date",
        "last_renewal_date",
    )

    list_filter = (
        "status",
        "joined_date",
        "last_renewal_date",
    )


@admin.register(MembershipType)
class MembershipTypeAdmin(SummernoteModelAdmin):
    summernote_fields = ("benefits",)
