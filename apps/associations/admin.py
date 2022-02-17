from django.contrib import admin

from apps.associations.models import Association


class AssociationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Association, AssociationAdmin)
