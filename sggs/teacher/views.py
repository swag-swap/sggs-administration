from django.shortcuts import render, redirect, get_object_or_404
from .forms import TeacherDetailsForm, AttendanceExtractionForm, QuestionForm
from administration.models import Student, Teacher, Notification, ClassSession, Subject, UploadedImage
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
    if request.user.is_teacher == 1:
        return render(request, 'base/404.html')
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question_data = {
                'author': request.user.id,
                'question': form.cleaned_data['question'].replace("'", "''"),  
                'option1': form.cleaned_data['option1'].replace("'", "''"),  
                'option2': form.cleaned_data['option2'].replace("'", "''"),  
                'option3': form.cleaned_data['option3'].replace("'", "''"),  
                'option4': form.cleaned_data['option4'].replace("'", "''"),  
                'correct_option': form.cleaned_data['correct_option'],
                'explanation': form.cleaned_data['explanation'].replace("'", "''"),  
            }
            
            cursor = connection.cursor()
            
            for field_name in ['question_image', 'option1_image', 'option2_image', 'option3_image', 'option4_image', 'explanation_image']:
                image_file = form.cleaned_data[field_name]

                if image_file:
                    upload_image = UploadedImage(image=image_file)
                    upload_image.save()
                    question_data[field_name] = upload_image.id
                else:
                    question_data[field_name] = 'NULL'

            table_name = subject.subjects_question_table_name

            # print("Table Name:", table_name)   

            query = f""" 
            INSERT INTO {table_name}  (author, question, option1, option2, option3, option4, correct_option, explanation, question_image, option1_image, option2_image, option3_image, option4_image, explanation_image)  VALUES ({question_data['author']}, '{question_data['question']}', '{question_data['option1']}', '{question_data['option2']}', '{question_data['option3']}', '{question_data['option4']}', {question_data['correct_option']}, '{question_data['explanation']}', {question_data['question_image']}, {question_data['option1_image']}, {question_data['option2_image']}, {question_data['option3_image']},  {question_data['option4_image']}, {question_data['explanation_image']}) 
            """

            # print("Query:", query)  
            cursor.execute(query)
            
            return redirect('teacher_add_question', subject_id=subject_id)
    else:
        form = QuestionForm()
    
    return render(request, 'teacher/add_question.html', {'is_teacher': True, 'user': request.user, 'form': form, 'subject': subject})

def delete_question_images(question_table_name, question_id):
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT 
            question_image, 
            option1_image, 
            option2_image, 
            option3_image, 
            option4_image, 
            explanation_image
        FROM 
            {question_table_name}
        WHERE 
            id = {question_id}
    """)
    image_ids = cursor.fetchone()
    if image_ids:
        for id in image_ids:
            if id is not None:
                uploaded_image = UploadedImage.objects.get(id=id)
                uploaded_image.delete()
        print("Deleted all question images")


def teacher_delete_question(request, subject_id, question_id): 
    subject = get_object_or_404(Subject, id=subject_id) 
    question_table_name = subject.subjects_question_table_name   
    delete_question_images(question_table_name, question_id)

    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {question_table_name} WHERE id = {question_id};")
 
    return redirect('teacher_add_question', subject_id=subject_id) 

def subject_questions(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id) 
    question_table_name = subject.subjects_question_table_name   

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {question_table_name}")

    rows = cursor.fetchall()

    # for row in rows:
    #     print(row)  

    return render(request, 'teacher/subject_questions.html', {'is_teacher':True, 'user':request.user,'rows': rows, 'subject':subject})