import uuid

from django.db import models


class UUIDModelMixin(models.Model):
    id = models.UUIDField(db_index=True, primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreateUpdateDateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
