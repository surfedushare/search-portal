"""
This module provides django admin functionality for users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from rest_framework.authtoken.models import Token

from surf.apps.users import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    """
    Provides admin options and functionality for User model.
    """
    pass


@admin.register(models.SurfConextAuth)
class SurfConextAuthAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for SurfConextAuth model.
    """
    pass
