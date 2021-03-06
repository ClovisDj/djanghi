# Generated by Django 3.2.12 on 2022-02-26 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('associations', '0002_add_meeting'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipPaymentSatus',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('current_value', models.FloatField(default=0)),
                ('paid_percentage', models.FloatField(blank=True, null=True)),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_payments_status', to='associations.association')),
                ('membership_payment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_payments_status', to='associations.membercontributionfield')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_payments_status', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
