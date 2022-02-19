from django.contrib import admin

from apps.associations.models import Association, MemberContributionField


class AssociationAdmin(admin.ModelAdmin):
    pass


class MemberContributionFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'association_label', )

    @staticmethod
    def association_label(obj):
        return obj.association.label


admin.site.register(Association, AssociationAdmin)

admin.site.register(MemberContributionField, MemberContributionFieldAdmin)
