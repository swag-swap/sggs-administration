from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import connection
from django.utils.text import slugify
from administration.models import Student, Teacher, Notification, ClassSession, Subject, UploadedImage, CustomUser
import os

## User profile photo 
@receiver(post_delete, sender=CustomUser)
def delete_profile_photo(sender, instance, **kwargs):
    if instance.profile_photo:
        if os.path.isfile(instance.profile_photo.path):
            os.remove(instance.profile_photo.path)


## Subject signals
@receiver(pre_save, sender=Subject)
def subject_pre_save(sender, instance, **kwargs):
    if instance.pk:   
        old_instance = Subject.objects.get(pk=instance.pk) 
        instance._old_name = old_instance.name

@receiver(post_save, sender=Subject)
def subject_post_save(sender, instance, created, **kwargs):
    table_name_prefix = "question_" 

    if hasattr(instance, '_old_name') and instance._old_name != instance.name:
        old_table_name = f"{table_name_prefix}{slugify(instance._old_name).replace('-', '_')}"   
        new_table_name = f"{table_name_prefix}{slugify(instance.name).replace('-', '_')}"   
 
        cursor = connection.cursor()
        try:
            cursor.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};") 
            instance.subjects_question_table_name = new_table_name

            print(f"Renamed table from {old_table_name} to {new_table_name}")
        except Exception as e:
            print(f"Error renaming table: {e}")

        delattr(instance, '_old_name')
    elif created:   
        
        table_name = f"{table_name_prefix}{slugify(instance.name).replace('-', '_')}"  # Table name
        cursor = connection.cursor()
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    author INTEGER REFERENCES administration_customuser(id),
                    question TEXT,
                    question_image INTEGER REFERENCES administration_uploadedimage(id),
                    option1 TEXT,
                    option1_image INTEGER REFERENCES administration_uploadedimage(id),
                    option2 TEXT,
                    option2_image INTEGER REFERENCES administration_uploadedimage(id),
                    option3 TEXT,
                    option3_image INTEGER REFERENCES administration_uploadedimage(id),
                    option4 TEXT,
                    option4_image INTEGER REFERENCES administration_uploadedimage(id),
                    correct_option INTEGER,
                    explanation TEXT,
                    explanation_image INTEGER REFERENCES administration_uploadedimage(id)
                );
            """) 
            instance.subjects_question_table_name = table_name

            print(f"Created table {table_name} for subject {instance.name}")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")

@receiver(post_delete, sender=Subject)
def subject_post_delete(sender, instance, **kwargs):
    # Delete the corresponding table
    table_name = f"question_{slugify(instance.name).replace('-', '_')}"
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Deleted table {table_name}")
    except Exception as e:
        print(f"Error deleting table {table_name}: {e}")




## Profile photo
@receiver(post_delete, sender=UploadedImage)
def delete_profile_photo(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)



## Session
@receiver(post_delete, sender=ClassSession)
def handle_class_session_post_delete(sender, instance, **kwargs):
    response_table_name = instance.response_table_name
    result_table_name = instance.result_table_name
    test_table_name = instance.test_table_name
    test_questions_table_name = instance.test_questions_table_name
    attendence_table_name = instance.attendence_table_name
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {response_table_name};")
        print(f"Dropping the table {response_table_name}...")
    except Exception as e:
        print(f"Error dropping table {response_table_name}: {e}")


    try:
        cursor.execute(f"DROP TABLE IF EXISTS {result_table_name};")
        print(f"Dropping the table {result_table_name}...")
    except Exception as e:
        print(f"Error dropping table {result_table_name}: {e}")


    try:
        cursor.execute(f"DROP TABLE IF EXISTS {test_table_name};")
        print(f"Dropping the table {test_table_name}...")
    except Exception as e:
        print(f"Error dropping table {test_table_name}: {e}")


    try:
        cursor.execute(f"DROP TABLE IF EXISTS {test_questions_table_name};")
        print(f"Dropping the table {test_questions_table_name}...")
    except Exception as e:
        print(f"Error dropping table {test_questions_table_name}: {e}")


    try:
        cursor.execute(f"DROP TABLE IF EXISTS {attendence_table_name};")
        print(f"Dropping the table {attendence_table_name}...")
    except Exception as e:
        print(f"Error dropping table {attendence_table_name}: {e}")
 