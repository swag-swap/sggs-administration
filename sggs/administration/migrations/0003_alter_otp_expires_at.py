# Generated by Django 4.2.11 on 2024-05-01 11:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_alter_notification_notification_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 1, 11, 43, 16, 55806, tzinfo=datetime.timezone.utc)),
        ),
    ]
