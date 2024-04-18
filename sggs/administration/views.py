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

def register(request):
    if request.method == 'POST':  
        form = RegistrationForm(request.POST)
        if form.is_valid():  
            cleaned_data = form.cleaned_data
            otp = cleaned_data.get('otp') 
            otp_instance = OTP.objects.filter(email=cleaned_data['email']).order_by('-created_at').first()
            if otp_instance:
                if otp_instance.is_valid() and otp == otp_instance.otp:
                    user = CustomUser.objects.create(
                        email=cleaned_data['email'],
                        username=cleaned_data['email'].split('@')[0], 
                        password=make_password(cleaned_data['password']),    
                        first_name=cleaned_data.get('first_name'),
                        last_name=cleaned_data.get('last_name')
                    ) 
                    if 'student' in cleaned_data['role'] :
                        Student.objects.create(user=user)
                        user.is_student = 0
                    if 'teacher' in cleaned_data['role'] :
                        Teacher.objects.create(user=user)
                        user.is_teacher = 0
                    if 'administrator' in cleaned_data['role'] :
                        Administrator.objects.create(user=user) 
                        user.is_administrator = 0
                    user.save()
                    otp_instance.delete()
                    return redirect('login')
                else:
                    if otp_instance.is_valid()==False:
                        otp_instance.delete()
                    form.add_error('otp', 'Invalid OTP. Please enter the correct OTP.')
            else:
                form.add_error('otp', 'No OTP found for this email address.')
        return render(request, 'administration/register.html', {'form': form}) 
    else:
        form = RegistrationForm()
    return render(request, 'administration/register.html', {'form': form})

@csrf_exempt
def get_otp(request):
    if request.method == 'GET':
        email = request.GET.get('email') 
        otp_instance = OTP.objects.filter(email=email).first()
        if otp_instance:
            if otp_instance.is_valid():
                return JsonResponse({'success': True, 'message': 'An active OTP already exists for this email.'})
            else:
                otp_instance.delete() 
        digits = "0123456789" 
        otp = ''.join(random.choice(digits) for _ in range(6))  
        # send_mail(
        #     'OTP for SGGS Administration!!',
        #     f'Your OTP for registration is: {otp}',
        #     'admin@sggs.ac.in', 
        #     [email],
        #     fail_silently=False,
        # )
        OTP.objects.create(email=email, otp=otp)
        return JsonResponse({'success': True, 'message': 'New OTP generated and sent to your email.'})
    return JsonResponse({'success': False})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            is_sggs = email.split('@')[1] 
            if not is_sggs == ('sggs.ac.in'):
                form.add_error('email', 'Please log in with your SGGS email address.')
                return render(request, 'administration/login.html', {'form': form})
            username = email.split('@')[0]  
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password, email=email)
            if user is not None:
                auth_login(request, user) 
                return redirect('login')
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'administration/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login') 

# Student views

@login_required
def edit_student_detail(request):
    student_instance = getattr(request.user, 'student_profile', None)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student_instance)
        if form.is_valid():
            student = form.save()
            student.user = request.user

            if request.user.is_superuser: 
                student.user.is_student = 1
            else: 
                send_approval_notification(student,'student')

            student.save()

            return redirect('notification_list')   
    else:
        form = StudentForm(instance=student_instance)

    return render(request, 'administration/edit_student_details.html', {'form': form})


# Teacher views

@login_required
def edit_teacher_detail(request):
    teacher_instance = getattr(request.user, 'teacher_profile')
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher_instance)
        if form.is_valid():
            teacher = form.save()
            teacher.user = request.user

            if request.user.is_superuser: 
                teacher.user.is_teacher = 1
                teacher.user.is_staff = True
            else: 
                send_approval_notification(teacher, 'teacher')

            teacher.save()

            return redirect('notification_list')   
    else:
        form = TeacherForm(instance=teacher_instance)

    return render(request, 'administration/edit_teacher_detail.html', {'form': form})


# Administrator views

@login_required
def edit_administrator_detail(request):
    administrator_instance = getattr(request.user, 'administrator_profile')
    
    if request.method == 'POST':
        form = AdministratorForm(request.POST, instance=administrator_instance)
        if form.is_valid():
            administrator = form.save()
            administrator.user = request.user

            if request.user.is_superuser: 
                administrator.user.is_administrator = 1
                administrator.user.is_superuser = True
            else: 
                send_approval_notification(administrator, 'administrator')

            administrator.save()

            return redirect('notification_list')   
    else:
        form = AdministratorForm(instance=administrator_instance)

    return render(request, 'administration/edit_administrator_detail.html', {'form': form})

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

