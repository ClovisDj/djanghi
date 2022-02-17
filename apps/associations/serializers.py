from rest_framework_json_api import serializers

from apps.associations.models import Association, MemberContributionField


class MemberContributionFieldModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberContributionField
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        exclude = (
            'association',
        )


class AssociationModelSerializer(serializers.ModelSerializer):
    member_contribution_fields = MemberContributionFieldModelSerializer(many=True)

    class Meta:
        model = Association
        read_only_fields = (
            'created_at',
            'updated_at',
        )
        exclude = (
            'registration_link_life',
        )
