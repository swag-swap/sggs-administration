# Generated by Django 4.2.11 on 2024-05-08 11:55

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_librarian_edited'),
        ('administration', '0011_notification_read_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='librarian',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='librarian_notification', to='library.librarian'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'Teacher Profile Update'), (2, 'New Teacher Request'), (3, 'New Student Enrollment'), (4, 'New Administrator Request'), (5, 'New Librarian Request'), (6, 'Exam Schedule'), (7, 'Attendance'), (8, 'Assignment Submission'), (9, 'Grading'), (10, 'System Maintenance'), (11, 'Student Profile Update'), (12, 'Fee Payment Reminder'), (13, 'Profile Approved'), (14, 'Profile Rejected'), (15, 'Class Session')], default=None, null=True),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 8, 12, 10, 17, 505643, tzinfo=datetime.timezone.utc)),
        ),
    ]
