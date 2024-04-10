# Generated by Django 4.2.11 on 2024-04-10 10:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_alter_otp_expires_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='subjects',
        ),
        migrations.RemoveField(
            model_name='classsession',
            name='teacher',
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 10, 10, 5, 22, 395912, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='classsession',
            name='teacher',
            field=models.ManyToManyField(related_name='session_teachers', to='administration.teacher'),
        ),
    ]