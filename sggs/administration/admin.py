from django.contrib import admin
from .models import CustomUser, Subject, Department, Teacher, Student, Semester, Administrator, Fee, ClassSession, Notification, OTP

admin.site.register(CustomUser)
admin.site.register(Subject)
admin.site.register(Department)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Semester) 
admin.site.register(Administrator)
admin.site.register(Fee) 
admin.site.register(ClassSession)
admin.site.register(Notification)
admin.site.register(OTP)
