# Generated by Django 5.0.3 on 2024-04-06 11:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_alter_administration_department_alter_otp_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 6, 11, 25, 52, 170127, tzinfo=datetime.timezone.utc)),
        ),
    ]
