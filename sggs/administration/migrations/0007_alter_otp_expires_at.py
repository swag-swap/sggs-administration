# Generated by Django 4.2.11 on 2024-05-05 07:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0006_alter_otp_expires_at_administrator_edited'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 5, 7, 33, 21, 345566, tzinfo=datetime.timezone.utc)),
        ),
    ]