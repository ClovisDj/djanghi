from django.db.utils import IntegrityError
from rest_framework_json_api import serializers

from apps.associations.models import Association, MemberContributionField


class MemberContributionFieldModelSerializer(serializers.ModelSerializer):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = getattr(self, 'context', {}).get('request')

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
