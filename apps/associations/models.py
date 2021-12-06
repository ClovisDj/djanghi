from django.conf import settings
from django.db import models

from apps.utils import CreateUpdateDateMixin, UUIDModelMixin


class Association(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)
    # To be used for authentication Ex. Mebam
    label = models.CharField(db_index=True, max_length=30, null=False, unique=True)

    # Association's contact info
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone_number = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, default='USA')
    address = models.CharField(max_length=200, null=True, blank=True)

    # Settings
    email_from = models.EmailField(null=False, unique=True)
    registration_link_life = models.IntegerField(default=settings.DEFAULT_REGISTRATION_LINK_LIKE)

    def __str__(self):
        return '[%s] %s object (%s)' % (self.label, self.__class__.__name__, self.pk)


class MemberContributionField(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    name = models.CharField(max_length=30, null=False)
    is_required = models.BooleanField(default=True)
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='member_contribution_fields')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'association'], name='unique_contribution_name_by_association')
        ]
