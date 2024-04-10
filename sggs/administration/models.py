from django.db import models, connection
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.contrib.admin.sites import site
from django.contrib import admin
from django.dispatch import receiver
import random, re

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

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    # subjects = models.ManyToManyField(Subject, related_name='departments')

@receiver(post_save, sender=Department)
def create_semesters(sender, instance, created, **kwargs):
    if created: 
        for i in range(1, 9):
            Semester.objects.create(name=i, department=instance)



class Semester(models.Model):
    name = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_semester') 

    def __str__(self):
        return f"{self.department.name} Semester {self.name}"

class Teacher(models.Model): 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    departments = models.ManyToManyField(Department, related_name='teachers', default=None) 

    def __str__(self):
        return self.user.username 

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
    teacher = models.ManyToManyField(Teacher, related_name='session_teachers') 
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    table_name = models.CharField(max_length=255, blank = True)
    
    def save(self, *args, **kwargs):
        department_name = self.semester.department.name
        subject_name = self.subject.name
        semester_name = f"Semester_{self.semester.name}"
        year = str(self.year)
        department_name = re.sub(r'\s+', '_', department_name)
        semester_name = re.sub(r'\s+', '_', semester_name)
        subject_name = re.sub(r'\s+', '_', subject_name)
        year = re.sub(r'\s+', '_', year)
        
        
        if self.table_name == '':
            table_name = f"attendence_{department_name}_{semester_name}_{year}_{subject_name}"
            self.table_name = table_name
            cursor = connection.cursor()
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES auth_user(id),
                        date DATE,
                        is_present BOOLEAN
                    );
                """)
                try:
                    class CustomModelAdmin(admin.ModelAdmin):
                        list_display = ('student_id', 'date', 'id_present') 
        
                        class Meta: 
                            verbose_name = f"{table_name} Entry"
                            verbose_name_plural = f"{table_name} Entries"
                    site.register(table_name, CustomModelAdmin)
                    print(f"Registering the table {table_name}...")
                except Exception as e:
                    print(f"Error Registering table {table_name}: {e}")
                print(f"Creating the table {table_name}...")
            except Exception as e:
                print(f"Error creating table {table_name}: {e}")
        else:
            old_table_name = self.table_name
            new_table_name = f"attendence_{department_name}_{semester_name}_{year}_{subject_name}"
            print(old_table_name, new_table_name)
            
            if old_table_name != new_table_name:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};")
                    self.table_name = new_table_name 
                    print(f"Updating table name from {old_table_name} to {new_table_name}...")
                except Exception as e:
                    print(f"Error updating table name: {e}")
        
        super().save(*args, **kwargs) 

@receiver(post_delete, sender=ClassSession)
def handle_class_session_post_delete(sender, instance, **kwargs):
    table_name = instance.table_name
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Dropping the table {table_name}...")
    except Exception as e:
        print(f"Error dropping table {table_name}: {e}")
 

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_notification', default=None, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_notification', default=None, null=True)
    administrator = models.ForeignKey(Administrator, on_delete=models.CASCADE, related_name='administrator_notification', default=None, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'