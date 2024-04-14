from django.db import models, connection
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.admin.sites import site
from django.contrib import admin
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.text import slugify
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
    name = models.CharField(max_length=100, unique=True)
    subjects_question_table_name = models.CharField(max_length=255, blank = True)

    def clean(self):
        lower_name = self.name.lower()
        if Subject.objects.exclude(pk=self.pk).filter(name__iexact=lower_name).exists():
            raise ValidationError('Subject with this name already exists.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Registering the model on admin dashboard
def create_dynamic_model(table_name, fields):
    meta_attrs = {'managed': False} 
    model_fields = {field_name: models.CharField(max_length=100) for field_name in fields} 
    dynamic_model = type(table_name, (models.Model,), {
        '__module__': __name__,
        'Meta': type('Meta', (), meta_attrs),
        **model_fields
    }) 
    return dynamic_model 

@receiver(pre_save, sender=Subject)
def subject_pre_save(sender, instance, **kwargs):
    if instance.pk:   
        old_instance = Subject.objects.get(pk=instance.pk) 
        instance._old_name = old_instance.name

@receiver(post_save, sender=Subject)
def subject_post_save(sender, instance, created, **kwargs):
    table_name_prefix = "question_" 

    if hasattr(instance, '_old_name') and instance._old_name != instance.name:
        old_table_name = f"{table_name_prefix}{slugify(instance._old_name)}"   
        new_table_name = f"{table_name_prefix}{slugify(instance.name)}"   
 
        cursor = connection.cursor()
        try:
            cursor.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};") 
            instance.subjects_question_table_name = new_table_name

            print(f"Renamed table from {old_table_name} to {new_table_name}")
        except Exception as e:
            print(f"Error renaming table: {e}")

        delattr(instance, '_old_name')
    elif created:   
        table_name = f"{table_name_prefix}{slugify(instance.name)}"  # Table name
        cursor = connection.cursor()
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    question TEXT,
                    question_image_path VARCHAR(255),
                    option1 TEXT,
                    option1_image_path VARCHAR(255),
                    option2 TEXT,
                    option2_image_path VARCHAR(255),
                    option3 TEXT,
                    option3_image_path VARCHAR(255),
                    option4 TEXT,
                    option4_image_path VARCHAR(255),
                    correct_option INTEGER,
                    explanation TEXT,
                    explanation_image_path VARCHAR(255)
                );
            """) 
            instance.subjects_question_table_name = table_name

            print(f"Created table {table_name} for subject {instance.name}")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")

@receiver(post_delete, sender=Subject)
def subject_post_delete(sender, instance, **kwargs):
    # Delete the corresponding table
    table_name = f"administration_question_{slugify(instance.name)}"
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Deleted table {table_name}")
    except Exception as e:
        print(f"Error deleting table {table_name}: {e}")


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

@receiver(post_save, sender=Department)
def create_semesters(sender, instance, created, **kwargs):
    if created: 
        for i in range(1, 9):
            Semester.objects.create(name=i, department=instance)



class Semester(models.Model):
    name = models.IntegerField() 

    def __str__(self):
        return f"{self.name}"

class Teacher(models.Model): 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    departments = models.ManyToManyField(Department, related_name='teachers', default=None) 

    def __str__(self):
        return self.user.username 

class Student(models.Model):  
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    reg_no = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_department', default=None, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_semester', default=None, null=True)
    year = models.IntegerField()
    roll_number = models.CharField(max_length=20, default='')
    date_of_birth = models.DateField(default='2000-01-01')
    address = models.TextField(default='')
    contact_number = models.CharField(max_length=15, default='') 

    def save(self, *args, **kwargs):
        if self.user.username:
            self.reg_no = self.user.username.upper()
        super().save(*args, **kwargs)

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
    total_active_days = models.IntegerField(default = 0)
    attendence_table_name = models.CharField(max_length=255, blank = True)
    result_table_name = models.CharField(max_length=255, blank = True)
    response_table_name = models.CharField(max_length=255, blank = True)
    test_table_name = models.CharField(max_length=255, blank = True)
    
    def save(self, *args, **kwargs):
        department_name = self.department.name
        subject_name = self.subject.name
        semester_name = f"Semester_{self.semester.name}"
        year = str(self.year)
        department_name = re.sub(r'\s+', '_', department_name)
        semester_name = re.sub(r'\s+', '_', semester_name)
        subject_name = re.sub(r'\s+', '_', subject_name)
        year = re.sub(r'\s+', '_', year)
        table_detail_name = f"z_{year}_{department_name}_{semester_name}_{subject_name}"
        
        
        if self.test_table_name == '':
            # Doing the attendence table creation
            attendence_table_name = f"{table_detail_name}_attendence"
            self.attendence_table_name = attendence_table_name
            cursor = connection.cursor()
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {attendence_table_name} (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES administration_student(id),
                        date DATE,
                        is_present BOOLEAN
                    );
                """)
                # try:
                #     class CustomModelAdmin(admin.ModelAdmin):
                #         list_display = ('student_id', 'date', 'id_present') 
        
                #         class Meta: 
                #             verbose_name = f"{table_name} Entry"
                #             verbose_name_plural = f"{table_name} Entries"
                #     site.register(table_name, CustomModelAdmin)
                #     print(f"Registering the table {table_name}...")
                # except Exception as e:
                #     print(f"Error Registering table {table_name}: {e}")
                print(f"Creating the table {attendence_table_name}...")
            except Exception as e:
                print(f"Error creating table {attendence_table_name}: {e}")

            # Doing the Test table creation
            test_table_name = f"{table_detail_name}_test"
            self.test_table_name = test_table_name
            cursor = connection.cursor()
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {test_table_name} (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES auth_user(id),
                        date DATE,
                        is_present BOOLEAN
                    );
                """) 
                print(f"Creating the table {test_table_name}...")
            except Exception as e:
                print(f"Error creating table {test_table_name}: {e}")

            # Doing the Result table creation
            result_table_name = f"{table_detail_name}_result"
            self.result_table_name = result_table_name
            cursor = connection.cursor()
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {result_table_name} (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES auth_user(id),
                        date DATE,
                        is_present BOOLEAN
                    );
                """) 
                print(f"Creating the table {result_table_name}...")
            except Exception as e:
                print(f"Error creating table {result_table_name}: {e}")

            # Doing the response table creation
            response_table_name = f"{table_detail_name}_response"
            self.response_table_name = response_table_name
            cursor = connection.cursor()
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {response_table_name} (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES auth_user(id),
                        date DATE,
                        is_present BOOLEAN
                    );
                """) 
                print(f"Creating the table {response_table_name}...")
            except Exception as e:
                print(f"Error creating table {response_table_name}: {e}")
        else:
            # Changing name of attendence table name
            old_attendence_table_name = self.attendence_table_name
            new_attendence_table_name = f"{table_detail_name}_attendence"
            print(old_attendence_table_name, new_attendence_table_name)
            
            if old_attendence_table_name != new_attendence_table_name:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"ALTER TABLE {old_attendence_table_name} RENAME TO {new_attendence_table_name};")
                    self.attendence_table_name = new_attendence_table_name 
                    print(f"Updating table name from {old_attendence_table_name} to {new_attendence_table_name}...")
                except Exception as e:
                    print(f"Error updating table name: {e}")

            # Changing name of Test table name
            old_test_table_name = self.test_table_name
            new_test_table_name = f"{table_detail_name}_test"
            print(old_test_table_name, new_test_table_name)
            
            if old_test_table_name != new_test_table_name:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"ALTER TABLE {old_test_table_name} RENAME TO {new_test_table_name};")
                    self.test_table_name = new_test_table_name 
                    print(f"Updating table name from {old_test_table_name} to {new_test_table_name}...")
                except Exception as e:
                    print(f"Error updating table name: {e}")

            #  Changing name of result table name
            old_result_table_name = self.result_table_name
            new_result_table_name = f"{table_detail_name}_result"
            print(old_result_table_name, new_result_table_name)
            
            if old_result_table_name != new_result_table_name:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"ALTER TABLE {old_result_table_name} RENAME TO {new_result_table_name};")
                    self.result_table_name = new_result_table_name 
                    print(f"Updating table name from {old_result_table_name} to {new_result_table_name}...")
                except Exception as e:
                    print(f"Error updating table name: {e}") 
            
            # Changing name of response table name
            old_response_table_name = self.response_table_name
            new_response_table_name = f"{table_detail_name}_response"
            print(old_response_table_name, new_response_table_name)
            
            if old_response_table_name != new_response_table_name:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"ALTER TABLE {old_response_table_name} RENAME TO {new_response_table_name};")
                    self.response_table_name = new_response_table_name 
                    print(f"Updating table name from {old_response_table_name} to {new_response_table_name}...")
                except Exception as e:
                    print(f"Error updating table name: {e}")
        
        super().save(*args, **kwargs) 

@receiver(post_delete, sender=ClassSession)
def handle_class_session_post_delete(sender, instance, **kwargs):
    response_table_name = instance.response_table_name
    result_table_name = instance.result_table_name
    test_table_name = instance.test_table_name
    attendence_table_name = instance.attendence_table_name
    cursor = connection.cursor()
    # Deleting the response table of the session
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {response_table_name};")
        print(f"Dropping the table {response_table_name}...")
    except Exception as e:
        print(f"Error dropping table {response_table_name}: {e}")


    # Deleting the response table of the session
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {result_table_name};")
        print(f"Dropping the table {result_table_name}...")
    except Exception as e:
        print(f"Error dropping table {result_table_name}: {e}")


    # Deleting the response table of the session
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {test_table_name};")
        print(f"Dropping the table {test_table_name}...")
    except Exception as e:
        print(f"Error dropping table {test_table_name}: {e}")


    # Deleting the response table of the session
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {attendence_table_name};")
        print(f"Dropping the table {attendence_table_name}...")
    except Exception as e:
        print(f"Error dropping table {attendence_table_name}: {e}")
 

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        (1, 'Teacher Profile Update'),
        (2, 'New Teacher Request'),
        (3, 'New Student Enrollment'),
        (4, 'Fee Payment Reminder'),
        (5, 'Class Session'),
        (6, 'Exam Schedule'),
        (7, 'Attendance'),
        (8, 'Assignment Submission'),
        (9, 'Grading'),
        (10, 'System Maintenance'),
        # Add more notification types as needed
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_notification', default=None, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_notification', default=None, null=True)
    administrator = models.ForeignKey(Administrator, on_delete=models.CASCADE, related_name='administrator_notification', default=None, null=True)
    for_student = models.BooleanField(default=False)
    for_administrator = models.BooleanField(default=False)
    for_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.message}'
