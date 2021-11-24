from django.contrib import admin

from core.models.search import Query


class QueryRankingAdminInline(admin.TabularInline):
    model = Query.users.through
    list_display = ("subquery", "freeze", "is_approved", "created_at", "modified_at")
    extra = 0


class QueryAdmin(admin.ModelAdmin):
    list_display = ("query", "created_at", "modified_at",)
    search_fields = ("query",)
    inlines = [QueryRankingAdminInline]
