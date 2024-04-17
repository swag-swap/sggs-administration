from django.contrib import admin
from django.db import models, connection
from .models import CustomUser, Subject, Department, Teacher, Student, Semester, Administrator, Fee, ClassSession, Notification, OTP, Division

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
admin.site.register(Division)


# from django.contrib import admin
# from django.apps import apps
# from .models import ClassSession


# # Step 1: Dynamically Create Model Classes
# def create_model_class(table_name, fields):
#     # Define the model class dynamically
#     meta_attrs = {'managed': False, 'db_table': table_name}
#     fields_dict = {field_name: models.CharField(max_length=100) for field_name in fields}
#     model_class = type(table_name, (models.Model,), {
#         '__module__': __name__,
#         **fields_dict,
#         'Meta': type('Meta', (), meta_attrs)
#     })
#     return model_class

# # Step 2: Dynamically Create Admin Classes
# def create_admin_class(model_class):
#     class DynamicAdmin(admin.ModelAdmin):
#         list_display = [field.name for field in model_class._meta.fields]

#     return DynamicAdmin

# # Step 3: Register Admin Classes
# def register_admin_classes(table_name, fields):
#     # Create model class
#     model_class = create_model_class(table_name, fields)
    
#     # Create admin class
#     admin_class = create_admin_class(model_class)
    
#     # Register admin class
#     admin.site.register(model_class, admin_class)

# # Example usage:
# def create_and_register_table(table_name, fields):
#     # Create table
#     # Perform table creation operation here
#     # For example, you can use raw SQL queries or Django's migration operations
    
#     # Register table with admin
#     register_admin_classes(table_name, fields)
 


# # Assuming you have the list of table names stored in the attendence_table_name, result_table_name, response_table_name, and test_table_name fields
# class_session = ClassSession.objects.first()

# if class_session:
#     tables = [class_session.attendence_table_name,
#               class_session.result_table_name,
#               class_session.response_table_name,
#               class_session.test_table_name]

#     for table_name in tables:
#         if table_name:
#             try:
#                 fields = ['student_id', 'date', 'is_present'] 
#                 create_and_register_table(table_name, fields)
#             except LookupError:
#                 print(f"Model class for table '{table_name}' not found.")
#                 continue 




# # Define a function to dynamically create a model
# def create_dynamic_model(table_name, fields):
#     # Define the attributes for the model's Meta class
#     meta_attrs = {'managed': False}

#     # Define the fields for the model
#     model_fields = {field_name: models.CharField(max_length=100) for field_name in fields}

#     # Create the model class using type()
#     dynamic_model = type(table_name, (models.Model,), {
#         '__module__': __name__,
#         'Meta': type('Meta', (), meta_attrs),
#         **model_fields
#     })

#     return dynamic_model


# # Assuming you have the name of the table stored in a variable
# table_name = 'question_oss'
# fields = ['question','question_image_path','option1','option1_image_path','option2','option2_image_path','option3','option3_image_path','option4','option4_image_path','explanation','explanation_image_path']  

# # Create the dynamic model
# dynamic_model = create_dynamic_model(table_name, fields)

# # Register the dynamic model with the admin
# admin.site.register(dynamic_model)

# from django.contrib import admin
# from django.db import models

# # Listen for Subject Creation Event (Example using Django signals)
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Subject

# @receiver(post_save, sender=Subject)
# def create_dynamic_models(sender, instance, created, **kwargs):
#     if created:
#         # Generate Models Dynamically based on the new subject
#         table_name = instance.name.lower().replace(' ', '_')
#         model_name = f'DynamicModel_{table_name}'
        
#         # Define fields for the dynamic model (you can customize this based on your requirements)
#         fields = {
#             'name': models.CharField(max_length=100),
#             # Add other fields as needed
#         }

#         # Create the dynamic model class
#         dynamic_model = type(model_name, (models.Model,), {
#             '__module__': __name__,
#             **fields
#         })

#         # Register the dynamic model with the admin
#         admin.site.register(dynamic_model)  