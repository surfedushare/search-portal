from django.contrib import admin

from core.models import ExtractionMapping


class JSONExtractionFieldAdminInline(admin.TabularInline):
    model = ExtractionMapping.json_fields.through
    fields = ("json_field", "property", "is_context")
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(json_field__isnull=False)


class MethodExtractionFieldAdminInline(admin.TabularInline):
    model = ExtractionMapping.method_fields.through
    fields = ("method_field", "property", "is_context")
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(method_field__isnull=False)


class ExtractionMappingAdmin(admin.ModelAdmin):
    list_display = ("name", "root", "repository",)
    inlines = [JSONExtractionFieldAdminInline, MethodExtractionFieldAdminInline]


class ExtractionMethodAdmin(admin.ModelAdmin):
    list_display = ("method", "processor")
