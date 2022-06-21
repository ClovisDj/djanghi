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
    email_from = models.EmailField(null=False, default=settings.DEFAULT_FROM_EMAIL)
    registration_link_life = models.IntegerField(default=settings.DEFAULT_REGISTRATION_LINK_LIFE)
    is_active = models.BooleanField(default=True)

    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updated_associations',
        null=True,
        blank=True
    )

    def __str__(self):
        return '[%s] %s object (%s)' % (self.label, self.__class__.__name__, self.pk)


class ContribFieldManager(models.Manager):
    def active(self):
        return self.filter(archived=False)

    def archived(self):
        return self.filter(archived=True)


class MemberContributionField(CreateUpdateDateMixin, UUIDModelMixin, models.Model):
    name = models.CharField(max_length=30, null=False)
    is_required = models.BooleanField(default=True)
    required_amount = models.FloatField(null=True, blank=True)
    member_can_opt_in = models.BooleanField(default=False)
    archived = models.BooleanField(default=False, db_index=True)

    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='member_contribution_fields'
    )
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='archived_contribution_fields',
        null=True,
        blank=True
    )

    objects = ContribFieldManager()

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'association'],
                name='unique_contribution_name_by_association'
            )
        ]


class Meeting(CreateUpdateDateMixin,
              UUIDModelMixin,
              models.Model):

    scheduled_date = models.DateField(blank=False, null=False, db_index=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    address = models.CharField(max_length=500, null=True, blank=True)

    scope = models.TextField(blank=True, null=True)
    rapport = models.TextField(blank=True, null=True)

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hosted_meetings',
        null=True,
        blank=True
    )
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaded_meetings',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_meetings'
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updated_meetings'
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='meetings'
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ['-scheduled_date']
