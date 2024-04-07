from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
import random

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True) 
    # -1 -> role is not choosen, 0 -> role choosen but not admiteed by admin, 1 -> role fixed
    is_student = models.IntegerField(default = -1)
    is_teacher = models.IntegerField(default = -1)
    is_administrator = models.IntegerField(default = -1) 

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5))  

    def is_valid(self):
        return self.expires_at > timezone.now()

class Subject(models.Model):
    name = models.CharField(max_length=100)

class Department(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, related_name='departments')

class Semester(models.Model):
    name = models.IntegerField()
    subjects = models.ManyToManyField(Subject, related_name='semesterSubjects')
    Department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_semester')


class Teacher(models.Model): 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    departments = models.ManyToManyField(Department, related_name='teachers', default=None) 

class Student(models.Model):  
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_department', default=None, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_semester', default=None, null=True)
    roll_number = models.CharField(max_length=20, default='')
    date_of_birth = models.DateField(default='2000-01-01')
    address = models.TextField(default='')
    contact_number = models.CharField(max_length=15, default='') 


class Fee(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='fee')
    year_1_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_2_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_3_fee = models.DecimalField(max_digits=10, decimal_places=2)
    year_4_fee = models.DecimalField(max_digits=10, decimal_places=2) 

class Administrator(models.Model): 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='administrator_profile')
    departments = models.ManyToManyField(Department, related_name='administrators', default=None) 

class ClassSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE) 
    start_date = models.DateField()
    end_date = models.DateField()

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_notification', default=None, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_notification', default=None, null=True)
    administrator = models.ForeignKey(Administrator, on_delete=models.CASCADE, related_name='administrator_notification', default=None, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'