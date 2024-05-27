from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse, QueryDict, HttpResponseRedirect, Http404, HttpResponse
from administration.models import *
from teacher.models import *
from student.models import *
from library.models import *
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login  as auth_login
from django.contrib.auth import logout as auth_logout
import logging, json, random
from django.db import transaction, connection


logger = logging.getLogger(__name__)



def home(request):
    if request.user.is_authenticated:
        user = request.user
        # if user.is_student == 1:
        #     return redirect('student_home')
        # elif user.is_teacher == 1:
        #     return redirect('teacher_home')
        # elif user.is_administrator == 1:
        #     return redirect('admin_home')
        if user.is_student == 0:
            processing_message = "Your request is being processed for student role."
        elif user.is_teacher == 0:
            processing_message = "Your request is being processed for teacher role."
        elif user.is_administrator == 0:
            processing_message = "Your request is being processed for administrator role."
        else:
            processing_message = "Your role is not determined yet."
        return render(request, 'sggs/home.html', {'processing_message': processing_message})
    else:
        return render(request, 'sggs/home.html')

def register(request):
    if request.method == 'POST':  
        form = RegistrationForm(request.POST)
        if form.is_valid():  
            cleaned_data = form.cleaned_data
            otp = cleaned_data.get('otp') 
            otp_instance = OTP.objects.filter(email=cleaned_data['email']).order_by('-created_at').first()
            print(otp, otp_instance.otp)
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
                        Student_edited.objects.create(user=user)
                        user.is_student = 0
                    if 'teacher' in cleaned_data['role'] :
                        Teacher_edited.objects.create(user=user)
                        user.is_teacher = 0
                    if 'administrator' in cleaned_data['role'] :
                        Administrator_edited.objects.create(user=user) 
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
        return render(request, 'sggs/register.html', {'form': form}) 
    else:
        form = RegistrationForm()
    return render(request, 'sggs/register.html', {'form': form})

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
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'sggs/login.html', {'form': form})

def logout(request):
    instructions = """
    <html>
    <body>
    <script>
        localStorage.clear();
        sessionStorage.clear();
        // cookies.clear();
        window.location.href = "/";
    </script>
    </body>
    </html>
    """ 
    auth_logout(request)
     
    return HttpResponse(instructions) 
 

# Student views

@login_required
def edit_student_detail(request):
    student_instance = getattr(request.user, 'student_edited_profile', None)
    
    if student_instance is None:
        student_instance = Student_edited.objects.create(user=request.user)

    student_obj = getattr(request.user, 'student_profile', None)
     
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student_instance)
        if form.is_valid():
            student = form.save()
            student.user = request.user

            if request.user.is_administrator: 
                student.user.is_student = 1
            else: 
                try:
                    previous_notification = Notification.objects.get(user=request.user, notification_type=3) 
                    previous_notification.message = 'Another edit done for student by user'
                    previous_notification.save()
                except Notification.DoesNotExist: 
                    Notification.objects.create(
                        user=request.user,
                        message='New Student request has been submitted.',
                        notification_type=3,
                        for_administrator=True
                    )               

            student.save()
            if student_obj:
                request.user.is_student = 2
            else:
                request.user.is_student = 0
            request.user.save()
            return redirect('home')   
    else:
        form = StudentForm(instance=student_instance)

    return render(request, 'sggs/edit_student_details.html', {'form': form})


# Teacher views

@login_required
def edit_teacher_detail(request):
    teacher_instance = getattr(request.user, 'teacher_edited_profile', None)
    if not teacher_instance:
        teacher_instance = Teacher_edited.objects.create(user=request.user)

    teacher_obj = getattr(request.user, 'teacher_profile', None)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher_instance)
        if form.is_valid():
            teacher = form.save()
            teacher.user = request.user

            if request.user.is_administrator: 
                teacher.user.is_teacher = 1
                teacher.user.is_staff = True
 
            else: 
                try:
                    previous_notification = Notification.objects.get(user=request.user, notification_type=2) 
                    previous_notification.message = 'Another edit for teacher done by user'
                    previous_notification.save()
                except Notification.DoesNotExist: 
                    Notification.objects.create(
                        user=request.user,
                        message='New teacher request has been submitted.',
                        notification_type=2,  
                        for_administrator=True
                    )

            teacher.save()
            if teacher_obj:
                request.user.is_teacher = 2
            else:
                request.user.is_teacher = 0
            
            request.user.save()

            return redirect('home')   
    else:
        form = TeacherForm(instance=teacher_instance)

    return render(request, 'sggs/edit_teacher_detail.html', {'form': form})


# Administrator views
@login_required
def edit_administrator_detail(request):
    administrator_instance = getattr(request.user, 'administrator_edited_profile', None)
    if not administrator_instance:
        administrator_instance = Administrator_edited.objects.create(user=request.user)

    administrator_obj = getattr(request.user, 'administrator_profile', None)

    
    if request.method == 'POST':
        form = AdministratorForm(request.POST, instance=administrator_instance)
        if form.is_valid():
            administrator = form.save()
            administrator.user = request.user

            if request.user.is_administrator: 
                administrator.user.is_administrator = 1
                administrator.user.is_superuser = True
            else: 
                try:
                    previous_notification = Notification.objects.get(user=request.user, notification_type=4) 
                    previous_notification.message = 'Another edit for Administrator done by user'
                    previous_notification.save()
                except Notification.DoesNotExist: 
                    Notification.objects.create(
                        user=request.user,
                        message='New Administrator request has been submitted.',
                        notification_type=4,  
                        for_administrator=True
                    )

            administrator.save()
            if administrator_obj:
                request.user.is_administrator = 2
            else:
                request.user.is_administrator = 0
            
            request.user.save()

            return redirect('home')   
    else:
        form = AdministratorForm(instance=administrator_instance)

    return render(request, 'sggs/edit_administrator_detail.html', {'form': form})


# Librarian views
@login_required
def edit_librarian_detail(request):
    librarian_instance = getattr(request.user, 'librarian_edited_profile', None)

    print(librarian_instance)

    if request.method == 'POST':
        if not librarian_instance:
            librarian_instance = Librarian_edited.objects.create(user=request.user)

        librarian_obj = getattr(request.user, 'librarian_profile', None)

        form = LibrarianForm(request.POST, instance=librarian_instance)
        if form.is_valid():
            librarian = form.save()
            librarian.user = request.user

            if request.user.is_administrator: 
                librarian.user.is_librarian = 1
                librarian.user.is_superuser = True
            else: 
                try:
                    previous_notification = Notification.objects.get(user=request.user, notification_type=5) 
                    previous_notification.message = 'Another edit for Librarian done by user'
                    previous_notification.save()
                except Notification.DoesNotExist: 
                    Notification.objects.create(
                        user=request.user,
                        message='New Librarian request has been submitted.',
                        notification_type=5,  
                        for_administrator=True
                    )

            librarian.save()
            if librarian_obj:
                request.user.is_librarian = 2
            else:
                request.user.is_librarian = 0
            
            request.user.save()

            return redirect('home')   
    else:
        form = LibrarianForm(instance=librarian_instance)

    return render(request, 'sggs/edit_librarian_details.html', {'form': form})
