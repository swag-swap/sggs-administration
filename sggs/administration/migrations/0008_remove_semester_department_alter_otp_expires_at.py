# Generated by Django 4.2.11 on 2024-04-10 10:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0007_alter_otp_expires_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='department',
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 10, 11, 1, 16, 942808, tzinfo=datetime.timezone.utc)),
        ),
    ]
