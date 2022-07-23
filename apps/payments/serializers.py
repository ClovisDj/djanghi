import copy

from rest_framework_json_api import serializers

from apps.associations.serializers import MemberContributionFieldModelSerializer
from apps.mixins import SerializerRequestInitMixin
from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.profiles.models import User
from apps.profiles.serializers import BaseUserModelSerializer, IncludedUserModelSerializer


class BaseMembershipPaymentModelSerializer(SerializerRequestInitMixin,
                                           serializers.ModelSerializer):
    membership_payment_type_id = serializers.UUIDField(required=True)
    payment_type = serializers.ChoiceField(
        choices=MembershipPayment.PAYMENT_TYPE,
        default=MembershipPayment.PAYMENT
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance or (self.request and self.request.method != 'POST'):
            # This field is only required for payment creation
            self.fields.pop('membership_payment_type_id', None)

    @staticmethod
    def validate_amount(amount):
        if amount and amount < 0:
            raise serializers.ValidationError('Should provide a positive value')
        return amount


class MembershipPaymentModelSerializer(BaseMembershipPaymentModelSerializer):
    class JSONAPIMeta:
        included_resources = ('membership_payment_type', 'author', )

    included_serializers = {
        'membership_payment_type': MemberContributionFieldModelSerializer,
        'author': IncludedUserModelSerializer,
    }

    def create(self, validated_data):
        validated_data['user_id'] = self.extract_user_id_from_nested_route()
        validated_data['author'] = self.request.user
        validated_data['association'] = self.request.user.association

        return super().create(validated_data)


class BulkMembershipPaymentModelSerializer(BaseMembershipPaymentModelSerializer):
    for_all_users = serializers.BooleanField(required=False, default=False)
    user_ids = serializers.ListSerializer(
        child=serializers.UUIDField(),
        required=False
    )

    def validate_user_ids(self, user_ids):
        valid_user_ids = User.objects\
            .for_association(association=self.request.user.association)\
            .filter(is_active=True, id__in=user_ids)\
            .values_list('id', flat=True)
        return valid_user_ids

    def validate(self, attrs):
        for_all_user = attrs.get('for_all_users')
        user_ids = attrs.get('user_ids', [])

        if not len(user_ids) > 0 and not for_all_user:
            raise serializers.ValidationError({
                'user_ids': 'Should Provide at least one valid user'
            })

        if for_all_user:
            attrs['user_ids'] = User.objects.for_association(association=self.request.user.association)\
                .filter(is_active=True).values_list('id', flat=True)

        return attrs

    def create(self, validated_data):
        create_data = copy.deepcopy(validated_data)
        create_data.pop('user_ids', None)
        create_data.pop('for_all_users', None)
        create_data['author'] = self.request.user
        create_data['association'] = self.request.user.association

        created_objs = []
        for user_id in validated_data['user_ids']:
            create_data['user_id'] = user_id
            created_objs.append(self.Meta.model.objects.create(**create_data))

        return created_objs[0]


class MembershipPaymentSatusModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MembershipPaymentSatus
        fields = '__all__'

    class JSONAPIMeta:
        included_resources = ('membership_payment_type', 'user')

    included_serializers = {
        'membership_payment_type': MemberContributionFieldModelSerializer,
        'user': BaseUserModelSerializer,
    }
