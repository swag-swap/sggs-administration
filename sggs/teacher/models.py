from django.db import models
from administration.models import *

class Teacher_edited(models.Model): 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_edited_profile')
    departments = models.ManyToManyField(Department, related_name='teachers_edited_department', default=None) 
    subjects = models.ManyToManyField(Subject, related_name='teacher_edited_subject', default=None) 

    def __str__(self):
        return self.user.username 
