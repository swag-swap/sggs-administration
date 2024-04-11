# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdministrationAdministrator(models.Model):
    user = models.OneToOneField('AdministrationCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_administrator'


class AdministrationAdministratorDepartments(models.Model):
    administrator = models.ForeignKey(AdministrationAdministrator, models.DO_NOTHING)
    department = models.ForeignKey('AdministrationDepartment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_administrator_departments'
        unique_together = (('administrator', 'department'),)


class AdministrationClasssession(models.Model):
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    table_name = models.CharField(max_length=255)
    semester = models.ForeignKey('AdministrationSemester', models.DO_NOTHING)
    subject = models.ForeignKey('AdministrationSubject', models.DO_NOTHING)
    active = models.BooleanField()
    department = models.ForeignKey('AdministrationDepartment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_classsession'


class AdministrationClasssessionTeacher(models.Model):
    classsession = models.ForeignKey(AdministrationClasssession, models.DO_NOTHING)
    teacher = models.ForeignKey('AdministrationTeacher', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_classsession_teacher'
        unique_together = (('classsession', 'teacher'),)


class AdministrationCustomuser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    email = models.CharField(unique=True, max_length=254)
    is_student = models.IntegerField()
    is_teacher = models.IntegerField()
    is_administrator = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'administration_customuser'


class AdministrationCustomuserGroups(models.Model):
    customuser = models.ForeignKey(AdministrationCustomuser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AdministrationCustomuserUserPermissions(models.Model):
    customuser = models.ForeignKey(AdministrationCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class AdministrationDepartment(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'administration_department'


class AdministrationFee(models.Model):
    year_1_fee = models.DecimalField(max_digits=10, decimal_places=5)  
    year_2_fee = models.DecimalField(max_digits=10, decimal_places=5)  
    year_3_fee = models.DecimalField(max_digits=10, decimal_places=5)  
    year_4_fee = models.DecimalField(max_digits=10, decimal_places=5)  
    student = models.OneToOneField('AdministrationStudent', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_fee'


class AdministrationNotification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField()
    administrator = models.ForeignKey(AdministrationAdministrator, models.DO_NOTHING, blank=True, null=True)
    student = models.ForeignKey('AdministrationStudent', models.DO_NOTHING, blank=True, null=True)
    teacher = models.ForeignKey('AdministrationTeacher', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AdministrationCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_notification'


class AdministrationOtp(models.Model):
    email = models.CharField(unique=True, max_length=254)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'administration_otp'


class AdministrationQuestionOss(models.Model):
    id = models.TextField(primary_key=True, blank=True, null=True)  # This field type is a guess.
    question = models.TextField(blank=True, null=True)
    question_image_path = models.CharField(blank=True, null=True)
    option1 = models.TextField(blank=True, null=True)
    option1_image_path = models.CharField(blank=True, null=True)
    option2 = models.TextField(blank=True, null=True)
    option2_image_path = models.CharField(blank=True, null=True)
    option3 = models.TextField(blank=True, null=True)
    option3_image_path = models.CharField(blank=True, null=True)
    option4 = models.TextField(blank=True, null=True)
    option4_image_path = models.CharField(blank=True, null=True)
    correct_option = models.IntegerField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    explanation_image_path = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administration_question_oss'


class AdministrationQuestionTemp(models.Model):
    id = models.TextField(primary_key=True, blank=True, null=True)  # This field type is a guess.
    question = models.TextField(blank=True, null=True)
    question_image_path = models.CharField(blank=True, null=True)
    option1 = models.TextField(blank=True, null=True)
    option1_image_path = models.CharField(blank=True, null=True)
    option2 = models.TextField(blank=True, null=True)
    option2_image_path = models.CharField(blank=True, null=True)
    option3 = models.TextField(blank=True, null=True)
    option3_image_path = models.CharField(blank=True, null=True)
    option4 = models.TextField(blank=True, null=True)
    option4_image_path = models.CharField(blank=True, null=True)
    correct_option = models.IntegerField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    explanation_image_path = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administration_question_temp'


class AdministrationSemester(models.Model):
    name = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'administration_semester'


class AdministrationStudent(models.Model):
    roll_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    department = models.ForeignKey(AdministrationDepartment, models.DO_NOTHING, blank=True, null=True)
    semester = models.ForeignKey(AdministrationSemester, models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField(AdministrationCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_student'


class AdministrationSubject(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'administration_subject'


class AdministrationTeacher(models.Model):
    user = models.OneToOneField(AdministrationCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_teacher'


class AdministrationTeacherDepartments(models.Model):
    teacher = models.ForeignKey(AdministrationTeacher, models.DO_NOTHING)
    department = models.ForeignKey(AdministrationDepartment, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'administration_teacher_departments'
        unique_together = (('teacher', 'department'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AdministrationCustomuser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
