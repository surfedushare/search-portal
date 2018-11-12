from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from surf.apps.users import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    pass


@admin.register(models.SurfConextAuth)
class SurfConextAuthAdmin(DjangoUserAdmin):
    pass
