from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import StudentForm, RegistrationForm, LoginForm, TeacherForm, AdministratorForm, ClassSessionForm, SubjectForm, DepartmentForm, SessionFilterForm, StudentSearchForm
from django.http import JsonResponse, QueryDict
from .models import CustomUser, Administrator, Student, Notification, OTP, Teacher, ClassSession, Subject, Department, Semester
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login  as auth_login
from django.contrib.auth import logout as auth_logout
import logging, json, random
from django.db import transaction, connection


logger = logging.getLogger(__name__)


@login_required
def home(request):
    if request.user.is_administrator == 1:
        return render(request, 'administration/home.html', {'is_administration': True, 'user': request.user})
    else:
        return render(request, 'base/404.html')

@login_required
def session_add(request):
    if request.user.is_administrator == 1:
        if request.method == 'POST':
            form = ClassSessionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_session_list')  # Assuming you have a URL named 'session_list'
        else:
            form = ClassSessionForm()
        return render(request, 'administration/session_add.html', {'is_administration': True, 'user': request.user,'form': form})
    else:
        return render(request, 'base/404.html')
    
def session_edit(request, session_id):
    if request.user.is_administrator == 1:
        session = get_object_or_404(ClassSession, id=session_id)
        if request.method == 'POST':
            form = ClassSessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                return redirect('admin_session_list')  # Redirect to session list page
        else:
            form = ClassSessionForm(instance=session)
        return render(request, 'administration/session_edit.html', {'is_administration': True, 'user': request.user,'session':session,'form': form})
    else:
        return render(request, 'base/404.html')

def session_delete(request, session_id):
    if request.user.is_administrator == 1:
        session = get_object_or_404(ClassSession, id=session_id)
        if request.method == 'POST':
            session.delete()
            return redirect('admin_session_list')  # Redirect to session list page
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

def subject_add(request):
    if request.user.is_administrator == 1:
        if request.method == 'POST':
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_subject_list')  # Redirect to session list page after adding subject
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
                return redirect('admin_subject_list')  # Redirect to subject list page
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
            return redirect('admin_subject_list')  # Redirect to subject list page
        return render(request, 'administration/subject_delete.html', {'is_administration': True, 'user': request.user,'subject': subject})
    else:
        return render(request, 'base/404.html')

def subject_list(request):
    if request.user.is_administrator == 1:
        subjects = Subject.objects.all()
        return render(request, 'administration/subject_list.html', {'is_administration': True, 'user': request.user,'subjects': subjects})
    else:
        return render(request, 'base/404.html')


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
                return redirect('admin_department_list')  # Redirect to department list page
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
            return redirect('admin_department_list')  # Redirect to department list page
        return render(request, 'administration/department_delete.html', {'is_administration': True, 'user': request.user,'department': department})
    else:
        return render(request, 'base/404.html')

def department_list(request):
    if request.user.is_administrator == 1:
        departments = Department.objects.all()
        return render(request, 'administration/department_list.html', {'is_administration': True, 'user': request.user,'departments': departments})
    else:
        return render(request, 'base/404.html')



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
    sessions = ClassSession.objects.filter(department__in=departments, active=True)
    return render(request, 'administration/teacher_detail.html', {'is_administration': True, 'user': request.user,'teacher': teacher, 'sessions': sessions})



def calculate_attendance_percentage(session_id):
    session = ClassSession.objects.get(id=session_id)
    attendance_table_name = session.attendence_table_name 
        # Query all students belonging to the specified year and semester
    students = Student.objects.filter(semester=session.semester, year = session.year)

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
    sessions = ClassSession.objects.filter(year=student.year, semester=student.semester)
    
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




#Notifications

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

