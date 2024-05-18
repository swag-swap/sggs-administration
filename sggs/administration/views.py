from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from django.http import JsonResponse, QueryDict
from administration.models import *
from teacher.models import *
from student.models import *
from library.models import *
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login  as auth_login
from django.contrib.auth import logout as auth_logout
import logging, json, random
import pandas as pd
from django.db import transaction, connection


logger = logging.getLogger(__name__)


@login_required
def home(request):
    if request.user.is_administrator == 1:
        return render(request, 'administration/home.html', {'is_administration': True, 'user': request.user})
    else:
        return render(request, 'base/404.html')

# Session

@login_required
def session_add(request):
    if request.user.is_administrator >= 1:
        if request.method == 'POST':
            form = ClassSessionForm(request.POST)
            if form.is_valid():
                # print(form)
                new_session = form.save(commit=False)
                
                existing_sessions = ClassSession.objects.filter(
                    department=new_session.department,
                    subject=new_session.subject,
                    semester=new_session.semester,
                    year=new_session.year
                )
                if existing_sessions.exists():
                    error_message = "A session with the same department, subject, semester, and year already exists."
                    return render(request, 'administration/session_add.html', {'is_administration': True, 'user': request.user, 'form': form, 'error_message': error_message})
                else: 
                    new_session.save()
                    return redirect('admin_session_list') 
        else:
            form = ClassSessionForm()
        return render(request, 'administration/session_add.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')
    
def session_edit(request, session_id):
    if request.user.is_administrator == 1:
        session = get_object_or_404(ClassSession, id=session_id)
        if request.method == 'POST':
            form = EditClassSessionForm(request.POST, instance=session)
            if form.is_valid():
                # print(form)
                form.save()
                return redirect('admin_session_list')  
        else:
            form = EditClassSessionForm(instance=session)
        return render(request, 'administration/session_edit.html', {'is_administration': True, 'user': request.user,'session':session,'form': form})
    else:
        return render(request, 'base/404.html')

def session_delete(request, session_id):
    if request.user.is_administrator == 1:
        session = get_object_or_404(ClassSession, id=session_id)
        if request.method == 'POST':
            session.delete()
            return redirect('admin_session_list')
        return render(request, 'administration/session_delete.html', {'is_administration': True, 'user': request.user,'session': session})
    else:
        return render(request, 'base/404.html')

def session_list(request):
    if request.user.is_administrator == 1:
        form = SessionFilterForm(request.GET)
        sessions = ClassSession.objects.all()

        if form.is_valid():
            department = form.cleaned_data.get('department')
            semester = form.cleaned_data.get('semester')
            subject = form.cleaned_data.get('subject')

            if department:
                sessions = sessions.filter(department=department)
            if semester:
                sessions = sessions.filter(semester=semester)
            if subject:
                sessions = sessions.filter(subject=subject)
        return render(request, 'administration/session_list.html', {'is_administration': True, 'user': request.user,'sessions': sessions, 'form': form})
    else:
        return render(request, 'base/404.html')
    
@login_required
def session_student_add(request, session_id):
    if request.user.is_administrator < 1:
        return render(request, 'base/404.html')
    
    try:
        session = ClassSession.objects.get(id=session_id)
    except ClassSession.DoesNotExist: 
        return render(request, 'administration/session_student_add_from_excel.html', {'is_administration': True, 'user': request.user})

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file'] 
        try:
            excel_data = parse_excel(excel_file)
        except Exception as e: 
            errors = ['Error processing Excel file'] 
            messages.error(request, f"Error processing Excel file: {e}")
            return render(request, 'administration/session_student_add_from_excel.html', {'errors': errors, 'is_administration': True, 'user': request.user})
        
        added_students = []
        student_not_exist = []
        errors = []

        for row in excel_data: 
            email = row.get('Email', '').strip()
            sggs_mail = email.split('@')[1]
            reg_no = email.split('@')[0].upper()
            if not email and sggs_mail != 'sggs.ac.in':
                errors.append("Email is missing in one or more rows.")
                continue
            
            try:
                student = Student.objects.get(reg_no=reg_no)
            except Student.DoesNotExist: 
                student_not_exist.append(email)
                continue
              
            added_students.append(student)
        session.students.add(*added_students)
        
        return render(request, 'administration/session_student_add_from_excel.html', {'added_students': added_students, 'student_not_exist': student_not_exist, 'is_administration': True, 'user': request.user})
    
    return render(request, 'administration/session_student_add_from_excel.html', {'is_administration': True, 'user': request.user})


# Subject

def subject_add(request):
    if request.user.is_administrator == 1:
        if request.method == 'POST':
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_subject_list') 
        else:
            form = SubjectForm()
        return render(request, 'administration/subject_add.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')

def subject_edit(request, subject_id):
    if request.user.is_administrator == 1:
        subject = get_object_or_404(Subject, pk=subject_id)
        if request.method == 'POST':
            form = SubjectForm(request.POST, instance=subject)
            if form.is_valid():
                form.save()
                return redirect('admin_subject_list')  
        else:
            form = SubjectForm(instance=subject)
        return render(request, 'administration/subject_edit.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')

def subject_delete(request, subject_id):
    if request.user.is_administrator == 1:
        subject = get_object_or_404(Subject, pk=subject_id)
        if request.method == 'POST':
            subject.delete()
            return redirect('admin_subject_list') 
        return render(request, 'administration/subject_delete.html', {'is_administration': True, 'user': request.user,'subject': subject})
    else:
        return render(request, 'base/404.html')

def subject_list(request):
    if request.user.is_administrator == 1:
        subjects = Subject.objects.all()
        return render(request, 'administration/subject_list.html', {'is_administration': True, 'user': request.user,'subjects': subjects})
    else:
        return render(request, 'base/404.html')

# Department

def department_add(request):
    if request.user.is_administrator == 1:
        if request.method == 'POST':
            form = DepartmentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_department_list')  
        else:
            form = DepartmentForm()
        return render(request, 'administration/department_add.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')

def department_edit(request, department_id):
    if request.user.is_administrator == 1:
        department = get_object_or_404(Department, pk=department_id)
        if request.method == 'POST':
            form = DepartmentForm(request.POST, instance=department)
            if form.is_valid():
                form.save() 
                return redirect('admin_department_list')  
        else:
            form = DepartmentForm(instance=department)
        return render(request, 'administration/department_edit.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')

def department_delete(request, department_id):
    if request.user.is_administrator == 1:
        department = get_object_or_404(Department, pk=department_id)
        if request.method == 'POST':
            department.delete()
            return redirect('admin_department_list')  
        return render(request, 'administration/department_delete.html', {'is_administration': True, 'user': request.user,'department': department})
    else:
        return render(request, 'base/404.html')

def department_list(request):
    if request.user.is_administrator == 1:
        departments = Department.objects.all()
        return render(request, 'administration/department_list.html', {'is_administration': True, 'user': request.user,'departments': departments})
    else:
        return render(request, 'base/404.html')



# Teacher

@login_required
def add_teacher(request):
    return render(request, 'teacher/teacher_detail.html', {'is_teacher':True, 'user':request.user})

@login_required
def manage_teacher(request):
    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    
    administrator = Administrator.objects.get(user = request.user) 
    departments = administrator.departments.all()

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        action = request.POST.get('action')
        if action == 'remove_teacher_role':
            teacher = get_object_or_404(Teacher, id=teacher_id)
            teacher.user.is_teacher = -1 
            teacher.user.save()
            messages.success(request, f"Teacher role removed for {teacher.user.username}")

            teacher.delete()
        else:
            messages.error(request, "Invalid action")

    teachers = Teacher.objects.filter(departments__in=departments).distinct()
    
    return render(request, 'administration/teacher_manage.html', {'is_administration': True, 'user': request.user,'teachers': teachers})

@login_required
def teacher_details(request, teacher_id):
    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    administrator = Administrator.objects.get(user = request.user) 
    departments = administrator.departments.all()
    sessions = ClassSession.objects.filter(teacher=teacher, active=True)
    return render(request, 'administration/teacher_detail.html', {'is_administration': True, 'user': request.user,'teacher': teacher, 'sessions': sessions})

def add_teacher_from_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file'] 
        try:
            excel_data = parse_excel(excel_file)
        except Exception as e: 
            errors = ['Error processing Excel file'] 
            messages.error(request, f"Error processing Excel file: {e}")
            return render(request, 'administration/teacher_add.html', {'errors': errors, 'is_administration': True, 'user': request.user})
        
        added_users = []
        updated_users = []
        added_teachers = []
        updated_teachers = []
        errors = []

        for row in excel_data: 
            email = row.get('Email', '').strip().lower()
            if not email:
                errors.append("Email is missing in one or more rows.")
                continue

            first_name = row.get('First_name', '').strip().upper()
            middle_name = row.get('Middle_name', '').strip().upper()
            surname = row.get('Last_name', '').strip().upper()
            departments = [department.strip() for department in row.get('Departments', '').split(',')]
            subjects = [subject.strip() for subject in row.get('Subjects', '').split(',')] 
            username = email.split('@')[0]

            try: 
                user, created = CustomUser.objects.get_or_create(email=email, defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': surname,
                    'password': email,
                })

                if not created:
                    user.first_name = first_name
                    user.last_name = surname
                    user.username = username
                    user.save()
                    updated_users.append(user)
                else:
                    added_users.append(user)
                
                try:
                    teacher, created = Teacher.objects.get_or_create(user=user)
                    if not created:
                        teacher.departments.clear()
                        teacher.subjects.clear()
                        updated_teachers.append(teacher)
                    else:
                        added_teachers.append(teacher)

                    for department_name in departments:
                        department = Department.objects.filter(name__iexact=department_name).first()
                        if department:
                            teacher.departments.add(department)
                        else:
                            errors.append(f"Department '{department_name}' not found for email : {email}.")
                    
                    for subject_name in subjects:
                        subject = Subject.objects.filter(name__iexact=subject_name).first()
                        if subject:
                            teacher.subjects.add(subject)
                        else:
                            errors.append(f"Subject '{subject_name}' not found for email : {email}.")
                        
                    user.is_teacher = 1
                    user.save()
                    teacher.save()
                
                except Exception as e:
                    errors.append(f"Error processing teacher for user with email {email}: {e}")

            except Exception as e: 
                errors.append(f"Error processing user with email {email}: {e}")

        if errors:
            for error in errors:
                messages.error(request, error)

        context = {
            'added_users': added_users,
            'updated_users': updated_users,
            'added_teachers': added_teachers,
            'updated_teachers': updated_teachers,
            'errors': errors,
        }
        return render(request, 'administration/teacher_add.html', {'context': context, 'is_administration': True, 'user': request.user})

    return render(request, 'administration/teacher_add.html', {'is_administration': True, 'user': request.user})

def parse_excel(excel_file):
    try: 
        df = pd.read_excel(excel_file) 
        data = df.to_dict(orient='records')
        return data
    except Exception as e: 
        raise Exception(f"Error parsing Excel file: {str(e)}")


# Student

def add_student(request):
    return 0

def add_student_from_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            excel_data = parse_excel(excel_file)
        except Exception as e:
            errors = ['Error processing Excel file']
            messages.error(request, f"Error processing Excel file: {e}")
            return render(request, 'administration/student_add_from_excel.html', {'errors': errors, 'is_administration': True, 'user': request.user})

        added_users = []
        updated_users = []
        added_students = []
        updated_students = []
        added_fees = []
        updated_fees = []
        errors = []

        for row in excel_data:
            email = row.get('Email', '').strip().lower()
            if not email:
                errors.append("Email is missing in one or more rows.")
                continue

            first_name = row.get('First_name', '').strip().upper()
            middle_name = row.get('Middle_name', '').strip().upper()
            surname = row.get('Last_name', '').strip().upper()
            department_name = row.get('Department', '').strip()
            semester_name = row.get('Semester', '')
            year = int(row.get('Year', 2000))
            roll_number = row.get('Roll_number', '').strip()
            date_of_birth = row.get('Date_of_birth', '2000-01-01')
            address = row.get('Address', '').strip()
            contact_number = row.get('Contact_number', '')
            username = email.split('@')[0]
            year_1_fee = row.get('Year_1_Fee','')
            year_2_fee = row.get('Year_2_Fee','')
            year_3_fee = row.get('Year_3_Fee','')
            year_4_fee = row.get('Year_4_Fee','')

            department = Department.objects.filter(name__iexact=department_name).first()
            semester = Semester.objects.filter(name__iexact=semester_name).first()

            if not department:
                errors.append(f"Department '{department_name}' not found for email: {email}.")
                continue

            if not semester:
                errors.append(f"Semester '{semester_name}' not found for email: {email}.")
                continue

            try:
                user, created = CustomUser.objects.get_or_create(email=email, defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': surname,
                    'password': email,
                })

                if not created:
                    user.first_name = first_name
                    user.last_name = surname
                    user.username = username
                    user.save()
                    updated_users.append(user)
                else:
                    added_users.append(user)

                try:
                    student, created = Student.objects.get_or_create(user=user, defaults={
                        'reg_no': user.username.upper(),
                        'department': Department.objects.filter(name__iexact=department).first(),
                        'semester': Semester.objects.filter(name__iexact=semester).first(),
                        'year': year,
                        'roll_number': roll_number,
                        'date_of_birth': date_of_birth,
                        'address': address,
                        'contact_number': contact_number,
                    })

                    if not created:
                        student.reg_no = user.username.upper()
                        student.department = department
                        student.semester = semester
                        student.year = year
                        student.roll_number = roll_number
                        student.date_of_birth = date_of_birth
                        student.address = address
                        student.contact_number = contact_number
                        student.save()
                        updated_students.append(student)
                    else:
                        added_students.append(student)
                    user.is_student = 1
                    user.save()
                    try:
                        fee, fee_created = Fee.objects.get_or_create(student=student, defaults={
                            'year_1_fee': year_1_fee,
                            'year_2_fee': year_2_fee,
                            'year_3_fee': year_3_fee,
                            'year_4_fee': year_4_fee,
                        })

                        if not fee_created:
                            fee.year_1_fee = year_1_fee
                            fee.year_2_fee = year_2_fee
                            fee.year_3_fee = year_3_fee
                            fee.year_4_fee = year_4_fee
                            updated_fees.append(fee)
                        else:
                            added_fees.append(fee)

                    except Exception as e:
                        errors.append(f"Error processing fee for student with email {email}: {e}")

                except Exception as e:
                    errors.append(f"Error processing student for user with email {email}: {e}")

            except Exception as e:
                errors.append(f"Error processing user with email {email}: {e}")

        if errors:
            for error in errors:
                messages.error(request, error)

        context = {
            'added_users': added_users,
            'updated_users': updated_users,
            'added_students': added_students,
            'updated_students': updated_students,
            'added_fees': added_fees,
            'updated_fees': updated_fees,
            'errors': errors,
        }
        return render(request, 'administration/student_add_from_excel.html', {'context': context, 'is_administration': True, 'user': request.user})

    return render(request, 'administration/student_add_from_excel.html', {'is_administration': True, 'user': request.user})

    
def calculate_attendance_percentage(session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    attendance_table_name = session.attendence_table_name 
    
    students = session.students.all()
    print(students)

    cursor = connection.cursor()
    cursor.execute(f"SELECT student_id, COUNT(*) as total_attendances FROM {attendance_table_name} WHERE is_present = True GROUP BY student_id")
    attendance_data = cursor.fetchall()

    total_sessions = session.total_active_days  
    attendance_percentage = {}
    for student_id, total_attendances in attendance_data:
        student = Student.objects.get(id=student_id)
        attendance_percentage[student.user.username] = (total_attendances / total_sessions) * 100
    
    for student in students:
        username = student.user.username
        if username not in attendance_percentage:
            attendance_percentage[username] = 0
    
    return attendance_percentage

def session_attendance(request, session_id):
    session = ClassSession.objects.get(pk=session_id)
    attendance_percentage = calculate_attendance_percentage(session_id)
    return render(request, 'administration/session_attendence.html', {'is_administration': True, 'user': request.user,'session': session, 'attendance_percentage': attendance_percentage})

def manage_student(request):
    if request.method == 'POST':
        form = StudentSearchForm(request.POST)
        if form.is_valid():
            reg_no = form.cleaned_data['reg_no']
            student = get_object_or_404(Student, reg_no=reg_no.upper())
            return redirect('admin_student_manage_detail', id=student.id)
    else:
        form = StudentSearchForm()
    return render(request, 'administration/student_manage.html', {'is_administration': True, 'user': request.user,'form': form})

def get_student_attendance(student_id):
    student = Student.objects.get(pk=student_id)
    sessions = ClassSession.objects.filter(students = student)
    
    attendance_data = {}

    for session in sessions:
        attendance_table_name = session.attendence_table_name
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {attendance_table_name} WHERE student_id = {student_id} AND is_present = True")
        total_attendances = cursor.fetchone()[0]

        total_classes = 0   
        if total_classes > 0:
            attendance_percentage = (total_attendances / total_classes) * 100
        else:
            attendance_percentage = 0 
        attendance_data[session.id] = {
            'session_name': f"{session.year}_{session.department.name}_{session.semester.name}_{session.subject.name}",
            'total_attendances': total_attendances,
            'attendance_percentage': attendance_percentage
        }

    return attendance_data

def manage_student_detail(request, id):
    student = get_object_or_404(Student, pk=id)
    attendance_data = get_student_attendance(id)
    return render(request, 'administration/student_manage_detail.html', {
        'is_administration': True, 
        'user': request.user,
        'student': student,
        'attendance_data': attendance_data
    })


# Administration


def add_admin_from_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file'] 
        try:
            excel_data = parse_excel(excel_file)
        except Exception as e: 
            errors = ['Error processing Excel file'] 
            messages.error(request, f"Error processing Excel file: {e}")
            return render(request, 'administration/admin_add_from_excel.html', {'errors': errors, 'is_administration': True, 'user': request.user})
        
        added_users = []
        updated_users = []
        added_admins = []
        updated_admins = []
        errors = []

        for row in excel_data: 
            email = row.get('Email', '').strip().lower()
            if not email:
                errors.append("Email is missing in one or more rows.")
                continue

            first_name = row.get('First_name', '').strip().upper()
            middle_name = row.get('Middle_name', '').strip().upper()
            surname = row.get('Last_name', '').strip().upper()
            departments = [department.strip() for department in row.get('Departments', '').split(',')] 
            username = email.split('@')[0]

            try: 
                user, created = CustomUser.objects.get_or_create(email=email, defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': surname,
                    'password': email,
                })

                if not created:
                    user.first_name = first_name
                    user.last_name = surname
                    user.username = username
                    user.save()
                    updated_users.append(user)
                else:
                    added_users.append(user)
                
                try:
                    administrator, created = Administrator.objects.get_or_create(user=user)
                    if not created:
                        administrator.departments.clear() 
                        updated_admins.append(administrator)
                    else:
                        added_admins.append(administrator)

                    for department_name in departments:
                        department = Department.objects.filter(name__iexact=department_name).first()
                        if department:
                            administrator.departments.add(department)
                        else:
                            errors.append(f"Department '{department_name}' not found for email : {email}.")
                    
                    user.is_administrator = 1
                    user.save()
                    administrator.save()
                
                except Exception as e:
                    errors.append(f"Error processing Administrator for user with email {email}: {e}")

            except Exception as e: 
                errors.append(f"Error processing user with email {email}: {e}")

        if errors:
            for error in errors:
                messages.error(request, error)

        context = {
            'added_users': added_users,
            'updated_users': updated_users,
            'added_admins': added_admins,
            'updated_admins': updated_admins,
            'errors': errors,
        }
        return render(request, 'administration/admin_add_from_excel.html', {'context': context, 'is_administration': True, 'user': request.user})

    return render(request, 'administration/admin_add_from_excel.html', {'is_administration': True, 'user': request.user})


#Notifications

def notifications(request):
    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    # Student profile approve notifications
    student_profile_updates = Notification.objects.filter(notification_type=3, for_administrator=True)

    # Teacher profile approve notifications
    teacher_profile_updates = Notification.objects.filter(notification_type=2, for_administrator=True)

    # Administrator profile approve notifications
    administrator_profile_updates = Notification.objects.filter(notification_type=4, for_administrator=True)

    # Librarian profile approve notifications
    librarian_profile_updates = Notification.objects.filter(notification_type=5, for_administrator=True)

    return render(request, 'administration/view_notification.html', {
        'student_profile_updates': student_profile_updates,        
        'teacher_profile_updates': teacher_profile_updates, 
        'administrator_profile_updates': administrator_profile_updates,
        'librarian_profile_updates': librarian_profile_updates,
        'is_administration': True,
        'user': request.user,
    })

def approve_student_profile(request, user_id):
    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    

    if request.method == 'POST': 
        if 'approve' in request.POST: 
            change_user = get_object_or_404(CustomUser, id=user_id)
            student_edited = get_object_or_404(Student_edited, user=change_user) 
            fee_edited = get_object_or_404(Fee_edited, student_edited=student_edited)
             
            student, student_created = Student.objects.get_or_create(
                user=student_edited.user,
                defaults={
                    'reg_no': student_edited.reg_no,
                    'department': student_edited.department,
                    'semester': student_edited.semester,
                    'year': student_edited.year,
                    'roll_number': student_edited.roll_number,
                    'date_of_birth': student_edited.date_of_birth,
                    'address': student_edited.address,
                    'contact_number': student_edited.contact_number
                }
            )
 
            fee, fee_created = Fee.objects.get_or_create(
                student=student,
                defaults={
                    'year_1_fee': fee_edited.year_1_fee,
                    'year_2_fee': fee_edited.year_2_fee,
                    'year_3_fee': fee_edited.year_3_fee,
                    'year_4_fee': fee_edited.year_4_fee
                }
            )

            if not student_created or not fee_created: 
                student.reg_no = student_edited.reg_no
                student.department = student_edited.department
                student.semester = student_edited.semester
                student.year = student_edited.year
                student.roll_number = student_edited.roll_number
                student.date_of_birth = student_edited.date_of_birth
                student.address = student_edited.address
                student.contact_number = student_edited.contact_number
                student.save()

                fee.year_1_fee = fee_edited.year_1_fee
                fee.year_2_fee = fee_edited.year_2_fee
                fee.year_3_fee = fee_edited.year_3_fee
                fee.year_4_fee = fee_edited.year_4_fee
                fee.save()

 
            student_edited.delete()
            fee_edited.delete()

            change_user.is_student = 1
            change_user.save()
            Notification.objects.get(user=change_user, notification_type=3).delete()

            Notification.objects.create(
                user=request.user,
                message='Your profile has been approved.',
                notification_type=13,
                student=student,
            )
            print("Approved")

            return redirect('admin_home') 
        
        elif 'reject' in request.POST:
            # Handle rejection action
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_message = form.cleaned_data.get('rejection_message') 
                change_user = get_object_or_404(CustomUser, id=user_id)
                print('reject')
                try:
                    noti = Notification.objects.get(user=change_user, notification_type=3)
                    noti.delete()
                except :
                    return redirect('admin_home')
                
                Notification.objects.create(
                    user=request.user,
                    message=f'Your profile has been rejected. Reason: {rejection_message}',
                    notification_type=14,
                    to_user=change_user,
                )
                print("Rejected")
                return redirect('admin_home')   
        else:
            return redirect('approve_student_profile', user_id=user_id) 
    change_user = get_object_or_404(CustomUser, id=user_id)
    student_edited = get_object_or_404(Student_edited, user=change_user) 
    fee_edited = get_object_or_404(Fee_edited, student_edited=student_edited)
    form = RejectionForm()

    return render(request, 'administration/approve_student_profile.html', {
        'student': student_edited,
        'fee': fee_edited,
        'is_administrator': True,
        'user': request.user,
        'form': form
    })

def approve_teacher_profile(request, user_id):

    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    

    if request.method == 'POST': 
        if 'approve' in request.POST: 
            change_user = get_object_or_404(CustomUser, id=user_id)
            teacher_edited = get_object_or_404(Teacher_edited, user=change_user)  
             
            teacher, teacher_created = Teacher.objects.get_or_create(
                user=teacher_edited.user,
            ) 

            if not teacher_created :  
                teacher.departments.set(teacher_edited.departments.all()),
                teacher.subjects.set(teacher_edited.subjects.all()) 
                teacher.save() 

 
            teacher_edited.delete()

            change_user.is_teacher = 1
            change_user.save()
            Notification.objects.get(user=change_user, notification_type=2).delete()

            Notification.objects.create(
                user=request.user,
                message='Your profile has been approved.',
                notification_type=13,
                teacher=teacher,
            )
            print("Approved")

            return redirect('admin_home') 
        
        elif 'reject' in request.POST: 
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_message = form.cleaned_data.get('rejection_message') 
                print('reject')

                change_user = get_object_or_404(CustomUser, id=user_id)
                try:
                    noti = Notification.objects.get( user=change_user, notification_type=2)
                    noti.delete()
                except :
                    return redirect('admin_home')

                Notification.objects.create(
                    user=request.user,
                    message=f'Your profile has been rejected. Reason: {rejection_message}',
                    notification_type=14,
                    to_user=change_user,
                )
                print("Rejected")
                return redirect('admin_home')   
        else:
            return redirect('approve_teacher_profile', user_id=user_id) 
        
    change_user = get_object_or_404(CustomUser, id=user_id)
    teacher_edited = get_object_or_404(Teacher_edited, user=change_user) 
    form = RejectionForm()

    return render(request, 'administration/approve_teacher_profile.html', {
        'teacher': teacher_edited,
        'is_administrator': True,
        'user': request.user,
        'form': form
    })

def approve_administration_profile(request, user_id):

    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    

    if request.method == 'POST': 
        if 'approve' in request.POST: 
            change_user = get_object_or_404(CustomUser, id=user_id)
            administrator_edited = get_object_or_404(Administrator_edited, user=change_user)  
             
            administrator, administrator_created = Administrator.objects.get_or_create(
                user=administrator_edited.user,
            ) 

            if not administrator_created :  
                administrator.departments.set(administrator_edited.departments.all()),
                administrator.subjects.set(administrator_edited.subjects.all()) 
                administrator.save() 

 
            administrator_edited.delete()

            change_user.is_teacher = 1
            change_user.save()
            Notification.objects.get(user=change_user, notification_type=4).delete()

            Notification.objects.create(
                user=request.user,
                message='Your profile has been approved.',
                notification_type=13,
                administrator=administrator,
            )
            print("Approved")

            return redirect('admin_home') 
        
        elif 'reject' in request.POST: 
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_message = form.cleaned_data.get('rejection_message') 
                print('reject')

                change_user = get_object_or_404(CustomUser, id=user_id)
                try:
                    noti = Notification.objects.get(user=change_user, notification_type=4)
                    noti.delete()
                except :
                    return redirect('admin_home')
                
                Notification.objects.create(
                    user=request.user,
                    message=f'Your profile has been rejected. Reason: {rejection_message}',
                    notification_type=14,
                    to_user=change_user,
                )
                print("Rejected")
                return redirect('admin_home')   
        else:
            return redirect('approve_administration_profile', user_id=user_id) 
        
    change_user = get_object_or_404(CustomUser, id=user_id)
    administrator_edited = get_object_or_404(Administrator_edited, user=change_user) 
    form = RejectionForm()

    return render(request, 'administration/approve_administrator_profile.html', {
        'administrator': administrator_edited,
        'is_administration': True,
        'user': request.user,
        'form': form
    })

def approve_librarian_profile(request, user_id):

    if not request.user.is_administrator == 1:
        return render(request, 'base/404.html')  
    

    if request.method == 'POST': 
        if 'approve' in request.POST: 
            change_user = get_object_or_404(CustomUser, id=user_id)
            librarian_edited = get_object_or_404(Librarian_edited, user=change_user)  
             
            librarian, librarian_created = Librarian.objects.get_or_create(
                user=librarian_edited.user,
            ) 

            if not librarian_created :   
                librarian.save() 

 
            librarian_edited.delete()

            change_user.is_teacher = 1
            change_user.save()
            Notification.objects.get(user=change_user, notification_type=5).delete()

            Notification.objects.create(
                user=request.user,
                message='Your profile has been approved.',
                notification_type=13,
                librarian=librarian,
            )
            print("Approved")

            return redirect('admin_home') 
        
        elif 'reject' in request.POST: 
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_message = form.cleaned_data.get('rejection_message') 
                print('reject')

                change_user = get_object_or_404(CustomUser, id=user_id)
                try:
                    noti = Notification.objects.get(user=change_user, notification_type=5)
                    noti.delete()
                except :
                    return redirect('admin_home')
                
                Notification.objects.create(
                    user=request.user,
                    message=f'Your Librarian profile has been rejected. Reason: {rejection_message}',
                    notification_type=14,
                    to_user=change_user,
                )
                print("Rejected")
                return redirect('admin_home')   
        else:
            return redirect('approve_librarian_profile', user_id=user_id) 
        
    change_user = get_object_or_404(CustomUser, id=user_id)
    librarian_edited = get_object_or_404(Librarian_edited, user=change_user) 
    form = RejectionForm()

    return render(request, 'administration/approve_librarian_profile.html', {
        'librarian': librarian_edited,
        'is_administration': True,
        'user': request.user,
        'form': form
    })




def send_approval_notification(model, role):
    admin = Administrator.objects.first()
    if admin:
        admin_email = admin.user.email
        try:
            # send_mail(
            #     'New Student Submission for Approval',
            #     f'A new student {student.user.username} has submitted their information for approval. Please review and approve.',
            #     'your_email@example.com',  # Replace with a valid sender email address
            #     [admin_email],
            #     fail_silently=False,
            # ) 
            if(role == 'student'):
                existing_notification = Notification.objects.filter(student=model).exists()
                if not existing_notification:
                    Notification.objects.create(
                        user=admin.user,
                        message=f'Approval required: A new student {model.user.username} has submitted their information for approval.',
                        student=model
                    )
                logger.info(f"Notification email sent to {admin_email}")

            if (role == 'teacher'):
                existing_notification = Notification.objects.filter(teacher=model).exists()

                if not existing_notification:
                    Notification.objects.create(
                        user=admin.user,
                        message=f'Approval required: A new Teacher {model.user.username} has submitted their information for approval.',
                        teacher=model
                    )
                logger.info(f"Notification email sent to {admin_email}")
            if (role == 'administrator'):
                existing_notification = Notification.objects.filter(administrator=model).exists()

                if not existing_notification:
                    Notification.objects.create(
                        user=admin.user,
                        message=f'Approval required: A new administrator {model.user.username} has submitted their information for approval.',
                        administrator=model
                    )
                logger.info(f"Notification email sent to {admin_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    else:
        logger.warning("No administration user found in the database.")
 
@login_required
def notification_list(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = Notification.objects.get(id=notification_id)
            if notification.message == 'Approval Required':
                if notification.student:
                    student = Student.objects.get(user=request.user)
                    student.user.is_student = 1
                    student.user.save()
                    notification.delete()   
                    return JsonResponse({'success': True}) 
                if notification.teacher:
                    teacher = Teacher.objects.get(user=request.user)
                    teacher.user.is_teacher = 1
                    teacher.user.save()
                    notification.delete()   
                    return JsonResponse({'success': True}) 
                if notification.administrator:
                    administrator = Administrator.objects.get(user=request.user)
                    administrator.user.is_administrator = 1
                    administrator.user.save()
                    notification.delete()   
                    return JsonResponse({'success': True}) 
    notifications = request.user.notifications.all()
    return render(request, 'administration/notification_list.html', {'notifications': notifications})

@login_required
def approve_notification(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        action = request.POST.get('action')  
        if notification_id and action in ['approve', 'reject']:
            notification = get_object_or_404(Notification, id=notification_id) 
            if notification.message.startswith('Approval required'):
                if notification.student:
                    student = notification.student
                    if action == 'approve':
                        student.user.is_student = 1
                        student.user.save()
                    elif action == 'reject': 
                        student.delete()
                    notification.delete()
                    return JsonResponse({'success': True})
                if notification.teacher:
                    teacher = notification.teacher
                    if action == 'approve':
                        teacher.user.is_teacher = 1
                        teacher.user.save()
                    elif action == 'reject': 
                        teacher.delete()
                    notification.delete()
                    return JsonResponse({'success': True})
                if notification.administrator:
                    administrator = notification.administrator
                    if action == 'approve':
                        administrator.user.is_administrator = 1
                        administrator.user.save()
                    elif action == 'reject': 
                        administrator.delete()
                    notification.delete()
                    return JsonResponse({'success': True})
    return JsonResponse({'success': False})

