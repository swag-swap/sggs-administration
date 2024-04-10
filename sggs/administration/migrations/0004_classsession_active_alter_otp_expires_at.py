# Generated by Django 4.2.11 on 2024-04-10 10:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0003_remove_department_subjects_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsession',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 10, 10, 24, 16, 509010, tzinfo=datetime.timezone.utc)),
        ),
    ]
