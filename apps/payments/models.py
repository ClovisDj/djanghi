from django.conf import settings
from django.db import models

from apps.utils import CreateUpdateDateMixin, UUIDModelMixin


class PaymentBase(CreateUpdateDateMixin,
                  UUIDModelMixin,
                  models.Model):
    COST = 'COST'
    PAYMENT = 'PAYMENT'
    PAYMENT_TYPE = (
        (COST, 'Subtractive for the user'),
        (PAYMENT, 'Additive for the user'),
    )

    note = models.CharField(max_length=250, blank=True, null=True)
    payment_type = models.CharField(max_length=15, choices=PAYMENT_TYPE, default=PAYMENT)
    amount = models.FloatField(blank=False, null=False)

    class Meta:
        ordering = ['-created_at']
        abstract = True

    def save(self, *args, **kwargs):
        if self.payment_type == self.COST and self.amount > 0:
            self.amount = -1 * self.amount

        super().save(*args, **kwargs)


class MembershipPayment(PaymentBase):
    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='membership_payments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membership_payments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_membership_payments'
    )
    membership_payment_type = models.ForeignKey(
        'associations.MemberContributionField',
        on_delete=models.CASCADE,
        related_name='membership_payments'
    )


class MembershipPaymentSatus(CreateUpdateDateMixin,
                             UUIDModelMixin,
                             models.Model):

    current_value = models.FloatField(blank=False, null=False, default=0)
    paid_percentage = models.FloatField(blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membership_payments_status'
    )
    membership_payment_type = models.ForeignKey(
        'associations.MemberContributionField',
        on_delete=models.CASCADE,
        related_name='membership_payments_status'
    )
    association = models.ForeignKey(
        'associations.Association',
        on_delete=models.CASCADE,
        related_name='membership_payments_status'
    )
