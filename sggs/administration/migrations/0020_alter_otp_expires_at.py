# Generated by Django 4.2.11 on 2024-05-26 10:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0019_alter_otp_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 26, 11, 11, 13, 349726, tzinfo=datetime.timezone.utc)),
        ),
    ]
