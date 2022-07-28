from django.conf import settings
from django.db import IntegrityError
from rest_framework_json_api import serializers

from apps.associations.models import Association, MemberContributionField
from apps.mixins import SerializerRequestInitMixin


class MemberContributionFieldModelSerializer(SerializerRequestInitMixin,
                                             serializers.ModelSerializer):
    class Meta:
        model = MemberContributionField
        read_only_fields = (
            'created_at',
            'updated_at',
            'archived',
            'archived_by',
        )
        exclude = (
            'association',
        )

    def validate(self, attrs):
        contrib_field_qs = MemberContributionField.objects.active()
        exceeding_max_contrib_field = (
            self.instance is None
            and self.request
            and settings.MAX_PAGE_SIZE <= contrib_field_qs.filter(association=self.request.user.association).count()
        )
        if exceeding_max_contrib_field:
            raise serializers.ValidationError(f"Max {settings.MAX_PAGE_SIZE} active payment fields allowed")

        return attrs

    def create(self, validated_data):
        validated_data['association'] = self.request.user.association
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'name': f'A contribution field with name: {validated_data["name"]}, '
                                                       f'already exists'})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'name': f'A contribution field with name: {instance.name}, '
                                                       f'already exists'})


class AssociationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Association
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        exclude = (
            'registration_link_life',
        )
