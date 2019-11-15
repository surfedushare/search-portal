from django.contrib import admin

from surf.vendor.surfconext.models import PrivacyStatement, DataGoal


class DataGoalAdminInline(admin.TabularInline):
    model = DataGoal
    list_display = ("type", "is_active", "priority",)
    extra = 0


class PrivacyStatementAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active",)
    inlines = (DataGoalAdminInline,)


admin.site.register(PrivacyStatement, PrivacyStatementAdmin)
