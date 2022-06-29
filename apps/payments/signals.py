from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.payments.models import MembershipPayment, MembershipPaymentSatus
from apps.utils import send_html_templated_email


@receiver(post_save, sender=MembershipPayment)
def update_membership_payments_status(sender, instance, created, **kwargs):
    if created:
        status_object, is_created = MembershipPaymentSatus.objects.get_or_create(
            user_id=instance.user_id,
            association_id=instance.association_id,
            membership_payment_type_id=instance.membership_payment_type_id
        )

        status_object.current_value += round(instance.amount, 2)

        required_amount = status_object.membership_payment_type.required_amount
        required_amount = required_amount if required_amount is not None else 0
        if required_amount > 0 and status_object.current_value > 0:
            status_object.paid_percentage = round((status_object.current_value / required_amount) * 100, 2)

        if status_object.current_value < 0:
            status_object.paid_percentage = 0

        status_object.save()

        if instance.user.can_receive_payment_notification:
            context = {
                "host": settings.API_HOST,
                "front_end_host": settings.FRONT_END_HOST,
                "association_label": instance.association.label,
                "first_name": instance.user.first_name,
                "payment_amount": instance.amount,
                "current_date": timezone.now().date().strftime('%m/%d/%Y'),
                "contrib_field": instance.membership_payment_type.name,
                "required_amount": required_amount,
                "total_paid": status_object.current_value,
                "unpaid": required_amount - status_object.current_value,
            }
            if instance.payment_type == MembershipPayment.COST:
                context['background_color'] = "rgb(253,82,116)"
                context['payment_type'] = "Debit"
            else:
                context['background_color'] = "rgb(54, 162, 235)"
                context['payment_type'] = "Credit"

            send_html_templated_email(
                [instance.user.email],
                'emails/membership-payment-notification.html',
                f'{instance.association.label.title()} - Payment notification',
                'payment-notification',
                context=context
            )
