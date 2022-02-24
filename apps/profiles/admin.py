from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.profiles.models import User


class UserRoleInline(admin.TabularInline):
    model = User.roles.through


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'association_label', 'is_registered', )
    list_display_links = ('username', )

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_registered', 'association', 'sex',)}),
    )

    inlines = [UserRoleInline]

    @staticmethod
    def association_label(obj):
        return obj.association.label


admin.site.register(User, CustomUserAdmin)
