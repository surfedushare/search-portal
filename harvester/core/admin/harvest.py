from django.contrib import admin

from core.models import HarvestSource


class HarvestSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "spec", "delete_policy", "created_at", "modified_at",)


class HarvestAdminInline(admin.TabularInline):
    model = HarvestSource.datasets.through
    fields = ("source", "harvested_at", "latest_update_at", "purge_after", "stage", "is_syncing",)
    readonly_fields = ("harvested_at",)
    extra = 0
