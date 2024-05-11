from django.db import models
from administration.models import *

class Student_edited(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_edited_profile')
    reg_no = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_edited_department', default=None, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_edited_semester', default=None, null=True)
    year = models.IntegerField(default=2000)
    roll_number = models.CharField(max_length=20, default='')
    date_of_birth = models.DateField(default='2000-01-01')
    address = models.TextField(default='')
    contact_number = models.CharField(max_length=15, default='') 

    def save(self, *args, **kwargs):
        if self.user.username:
            self.reg_no = self.user.username.upper()
        super().save(*args, **kwargs)

class Fee_edited(models.Model):
    student_edited = models.OneToOneField(Student_edited, on_delete=models.CASCADE, related_name='fee_edited')
    year_1_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_2_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_3_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_4_fee = models.DecimalField(max_digits=10, decimal_places=2) 