from django.contrib import admin

from core.models import ExtractionMapping


class JSONExtractionFieldAdminInline(admin.TabularInline):
    model = ExtractionMapping.json_fields.through
    fields = ("json_field", "property", "is_context", "is_protected")
    extra = 0

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return [field for field in fields if field != "is_protected"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(json_field__isnull=False)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(is_protected=False)


class MethodExtractionFieldAdminInline(admin.TabularInline):
    model = ExtractionMapping.method_fields.through
    fields = ("method_field", "property", "is_context", "is_protected")
    extra = 0

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return [field for field in fields if field != "is_protected"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(method_field__isnull=False)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(is_protected=False)


class ExtractionMappingAdmin(admin.ModelAdmin):
    list_display = ("name", "root", "repository",)
    inlines = [JSONExtractionFieldAdminInline, MethodExtractionFieldAdminInline]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return fields
        return ["repository", "root"]


class ExtractionMethodAdmin(admin.ModelAdmin):
    list_display = ("method", "processor")
