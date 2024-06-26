# Generated by Django 4.2.11 on 2024-05-05 06:39

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_alter_otp_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 5, 6, 54, 7, 423572, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Administrator_edited',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departments', models.ManyToManyField(default=None, related_name='administrator_edited_department', to='administration.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='administrator_edited_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
