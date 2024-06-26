# Generated by Django 4.2.11 on 2024-05-10 13:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0012_notification_librarian_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsession',
            name='students',
            field=models.ManyToManyField(related_name='session_students', to='administration.student'),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 10, 13, 51, 35, 918254, tzinfo=datetime.timezone.utc)),
        ),
    ]
