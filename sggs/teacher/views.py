from django.shortcuts import render, redirect, get_object_or_404
from .forms import TeacherDetailsForm, AttendanceExtractionForm, QuestionForm, ImageUploadForm
from administration.models import Student, Teacher, Notification, ClassSession, Subject
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pandas as pd
import os
from django.http import JsonResponse
from django.db import  connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


@login_required
def  teacher_home(request): 
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    teacher = Teacher.objects.get(user=request.user) 
    sessions = teacher.session_teachers.all()
    context = {'is_teacher':True, 'user':request.user,'teacher': teacher, 'sessions': sessions}
    return render(request, 'teacher/home.html', context)

@login_required
def edit_profile(request):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    teacher = Teacher.objects.get(user=request.user)
    if request.method == 'POST':
        form = TeacherDetailsForm(request.POST, instance=teacher)
        if form.is_valid():
            form.instance.user = request.user
            teacher = form.save()
            existing_notification = Notification.objects.filter( 
                notification_type=1
            ).first()

            if existing_notification:
                existing_notification.delete()   

            Notification.objects.create(
                user=request.user,   
                message=f"Teacher profile update: {teacher.user.username}",
                notification_type=1,  
                for_administrator = True
            )
            return redirect('admin_home')  
    else:
        form = TeacherDetailsForm(instance=teacher)
    return render(request, 'teacher/edit_profile.html', {'is_teacher':True, 'user':request.user,'form': form}) 

def start_attendence(request, session_id):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    session = get_object_or_404(ClassSession, pk=session_id)
    session.attendence_active = True
    session.save()
    Notification.objects.create(
            user = request.user,
            message=f'Attendance is now active for session {session.id}',
            notification_type=7,
            session=session,
            for_student=True
        )
    return redirect('teacher_home')

def stop_attendence(request, session_id):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    session = get_object_or_404(ClassSession, pk=session_id)
    session.attendence_active = False
    session.save()
    Notification.objects.filter(session=session, notification_type=7).delete()

    return redirect('teacher_home')

def take_attendance(request, session_id):
    session = get_object_or_404(ClassSession, pk=session_id)
    
    if request.method == 'POST': 
        excel_file = request.FILES['excel_file']
        attendance_date = request.POST['attendance_date'] 
        df = pd.read_excel(excel_file) 
        cursor = connection.cursor()
         
        for index, row in df.iterrows():
            reg_no = row['Registration Number']  
            is_present = row['is_present']   
            if is_present:
                is_present = 1
            else :
                is_present = 0
            
            print(reg_no, is_present)
            
            try:
                student = Student.objects.get(reg_no=reg_no)
                student_id = student.id
                print(student_id)
            except Student.DoesNotExist:
                return JsonResponse({'error': f'Student with registration number {reg_no} not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
            
            try: 
                cursor.execute(f""" INSERT INTO {session.attendence_table_name} (student_id, date, is_present)   VALUES (?, ?, ?)   CONFLICT(student_id, date) DO UPDATE SET is_present = excluded.is_present""", (student_id, attendance_date, is_present))
            except Exception as e: 
                return JsonResponse({'error': str(e)}, status=500)
         
        
        return JsonResponse({'message': 'Attendance submitted successfully'})
    
    return render(request, 'teacher/attendance_take.html', {'is_teacher':True, 'user':request.user,'session': session})


def teacher_sessions(request):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    teacher = Teacher.objects.get(user=request.user) 
    sessions = teacher.session_teachers.all()
    return render(request, 'teacher/sessions.html', {'is_teacher':True, 'user':request.user,'sessions': sessions})

def subject_list(request):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    subjects = Subject.objects.all()
    return render(request, 'teacher/subject_list.html', {'is_teacher':True, 'user':request.user,'subjects': subjects})

def add_question(request, subject_id):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question_data = form.cleaned_data
            question_text = question_data['question']
            question_image = question_data.get('question_image')
            option1 = question_data['option1']
            option1_image = question_data.get('option1_image')
            option2 = question_data['option2']
            option2_image = question_data.get('option2_image')
            option3 = question_data['option3']
            option3_image = question_data.get('option3_image')
            option4 = question_data['option4']
            option4_image = question_data.get('option4_image')
            correct_option = question_data['correct_option']
            explanation = question_data['explanation']
            explanation_image = question_data.get('explanation_image')
            
            # Save images to the server
            if question_image:
                question_image_path = default_storage.save('question_images/' + question_image.name, ContentFile(question_image.read()))
            else:
                question_image_path = None
            
            if option1_image:
                option1_image_path = default_storage.save('option_images/' + option1_image.name, ContentFile(option1_image.read()))
            else:
                option1_image_path = None
            
            if option2_image:
                option2_image_path = default_storage.save('option_images/' + option2_image.name, ContentFile(option2_image.read()))
            else:
                option2_image_path = None
            
            if option3_image:
                option3_image_path = default_storage.save('option_images/' + option3_image.name, ContentFile(option3_image.read()))
            else:
                option3_image_path = None
            
            if option4_image:
                option4_image_path = default_storage.save('option_images/' + option4_image.name, ContentFile(option4_image.read()))
            else:
                option4_image_path = None
            
            if explanation_image:
                explanation_image_path = default_storage.save('explanation_images/' + explanation_image.name, ContentFile(explanation_image.read()))
            else:
                explanation_image_path = None

            print(question_text, question_image_path, option1, option1_image_path,  option2, option2_image_path, option3, option3_image_path, option4, option4_image_path,  correct_option, explanation, explanation_image_path, option1_image)
            
            # with connection.cursor() as cursor:
            #     cursor.execute("""
            #         INSERT INTO {table_name} (question, question_image_path, option1, option1_image_path, 
            #         option2, option2_image_path, option3, option3_image_path, option4, option4_image_path, 
            #         correct_option, explanation, explanation_image_path) 
            #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                # """.format(table_name=subject.subjects_question_table_name), 
                # [question_text, question_image_path, option1, option1_image_path, 
                # option2, option2_image_path, option3, option3_image_path, option4, option4_image_path, 
                # correct_option, explanation, explanation_image_path])
            
            return redirect('teacher_add_question', subject_id=subject_id)
    else:
        form = QuestionForm()
    
    return render(request, 'teacher/add_question.html', {'is_teacher':True, 'user':request.user,'form': form, 'subject': subject})


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            save_path = os.path.join('media', image.name)
            with open(save_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            return redirect('upload_image')
    else:
        form = ImageUploadForm()
    return render(request, 'teacher/upload.html', {'form': form})