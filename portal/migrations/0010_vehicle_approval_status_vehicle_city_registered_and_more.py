# Generated by Django 5.1.5 on 2025-02-09 14:04

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_image_alter_announcement_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('denied', 'denied')], default='pending', max_length=50),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='city_registered',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='portal.city'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='vehicle_documents/'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='end_date',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.CreateModel(
            name='VehicleApproval',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('review_status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('denied', 'denied')], default='pending', max_length=50)),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('rejection_reason', models.TextField(null=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.vehicle')),
            ],
        ),
    ]
