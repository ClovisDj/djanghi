from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.profiles.models import User, UserRole


class UserRoleInline(admin.TabularInline):
    model = User.roles.through


class CustomUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'association_label', 'is_registered')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_registered', 'association', )}),
    )

    inlines = [UserRoleInline]

    @staticmethod
    def association_label(obj):
        return obj.association.label


admin.site.register(User, CustomUserAdmin)
