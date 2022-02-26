from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import MembershipPayment, MembershipPaymentSatus


@receiver(post_save, sender=MembershipPayment)
def update_membership_payments_status(sender, instance, created, **kwargs):
    if created:
        status_object, is_created = MembershipPaymentSatus.objects.get_or_create(
            user_id=instance.user_id,
            association_id=instance.association_id,
            membership_payment_type_id=instance.membership_payment_type_id
        )
        status_object.current_value += round(instance.amount, 2) if instance.payment_type == MembershipPayment.PAYMENT \
            else (-1) * round(instance.amount, 2)

        required_amount = status_object.membership_payment_type.required_amount
        if required_amount and required_amount > 0 and status_object.current_value > 0:
            status_object.paid_percentage = round((status_object.current_value / required_amount) * 100, 2)

        if status_object.current_value < 0:
            status_object.paid_percentage = 0

        status_object.save()
