from rest_framework_json_api import serializers

from apps.associations.serializers import MemberContributionFieldModelSerializer
from apps.payments.models import MembershipPayment
from apps.profiles.serializers import UserModelSerializer


class MembershipPaymentModelSerializer(serializers.ModelSerializer):
    membership_payment_type_id = serializers.UUIDField(required=True)

    class Meta:
        model = MembershipPayment
        read_only_fields = (
            'created_at',
            'updated_at',
            'membership_payment_type',
            'association',
            'author',
            'user',
        )
        fields = '__all__'

    class JSONAPIMeta:
        included_resources = ('membership_payment_type', 'author', )

    included_serializers = {
        'membership_payment_type': MemberContributionFieldModelSerializer,
        'author': UserModelSerializer,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = getattr(self, 'context', {}).get('request')

        if self.instance or (self.request and self.request.method != 'POST'):
            # This field is only required for payment creation
            self.fields.pop('membership_payment_type_id', None)

    def extract_user_id_from_request(self):
        return self.request.parser_context['kwargs']['user_pk']

    def create(self, validated_data):
        validated_data['user_id'] = self.extract_user_id_from_request()
        validated_data['author'] = self.request.user
        validated_data['association'] = self.request.user.association

        return super().create(validated_data)
