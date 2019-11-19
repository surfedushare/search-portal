from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import messages
from surf.apps.users import models
from django.utils.safestring import mark_safe

@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    actions = ['export_user_data']

    def export_user_data(self, request, queryset):
        if len(queryset) > 1:
            messages.error(request, "Please export a single user at a time.")
            return
        user = queryset[0]
        result = user.get_all_user_data()
        messages.success(request, mark_safe(result))


    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if not request.user.is_superuser:
    #         # remove "only for admin" actions
    #         actions.pop('export_user_data', None)
