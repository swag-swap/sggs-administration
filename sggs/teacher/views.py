from django.shortcuts import render, redirect, get_object_or_404
from .forms import TeacherDetailsForm, AttendanceExtractionForm, QuestionForm, TestCreationForm
from administration.models import Student, Teacher, Notification, ClassSession, Subject, UploadedImage
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import pandas as pd
import os
from django.http import HttpResponse, JsonResponse
from django.db import  connection, transaction
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

@login_required
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

@login_required
def stop_attendence(request, session_id):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    session = get_object_or_404(ClassSession, pk=session_id)
    session.attendence_active = False
    session.save()
    Notification.objects.filter(session=session, notification_type=7).delete()

    return redirect('teacher_home')

@login_required
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

@login_required
def teacher_sessions(request):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    teacher = Teacher.objects.get(user=request.user) 
    sessions = teacher.session_teachers.all()
    return render(request, 'teacher/sessions.html', {'is_teacher':True, 'user':request.user,'sessions': sessions})

@login_required
def subject_list(request):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    subjects = Subject.objects.all()
    return render(request, 'teacher/subject_list.html', {'is_teacher':True, 'user':request.user,'subjects': subjects})

@login_required
def add_question(request, subject_id):
    if not request.user.is_teacher == 1:
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

@login_required
def delete_question_images(question_table_name, question_id):
    return 0

@login_required
def teacher_delete_question(request, subject_id, question_id): 
    subject = get_object_or_404(Subject, id=subject_id) 
    question_table_name = subject.subjects_question_table_name   
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
    print(question_table_name, question_id)
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {question_table_name} WHERE id = {question_id};")
    if image_ids:
        for id in image_ids:
            if id is not None:
                uploaded_image = UploadedImage.objects.get(id=id)
                uploaded_image.delete()
    print("Deleted all question images")
    return redirect('teacher_add_question', subject_id=subject_id) 

@login_required
def subject_questions(request, subject_id):
    if request.user.is_teacher == -1:
        render(request, 'base/404.html')
    subject = get_object_or_404(Subject, id=subject_id) 
    question_table_name = subject.subjects_question_table_name   

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {question_table_name}")

    rows = cursor.fetchall()

    # for row in rows:
    #     print(row)  

    return render(request, 'teacher/subject_questions.html', {'is_teacher':True, 'user':request.user,'rows': rows, 'subject':subject})


@login_required
def session_tests(request, session_id):
    if request.user.is_teacher == -1:
        return render(request, 'base/404.html') 
    session = ClassSession.objects.get(id=session_id)
    test_table_name = session.test_table_name
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {test_table_name}")
    columns = [col[0] for col in cursor.description]  
    tests = [dict(zip(columns, row)) for row in cursor.fetchall()] 
    
    return render(request, 'teacher/session_tests.html', {'is_teacher':True, 'user':request.user,'session': session, 'tests': tests})

@login_required
def test_create(request, session_id):
    if request.user.is_teacher == -1:
        return render(request, 'base/404.html') 
    session = ClassSession.objects.get(id=session_id)

    if request.method == 'POST':
        form = TestCreationForm(request.POST, initial={'subject_question_table_name': session.subject.subjects_question_table_name})
        if form.is_valid():
            heading = form.cleaned_data['heading']
            description = form.cleaned_data['description']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            no_of_questions = form.cleaned_data['no_of_questions']
            
            test_table_name = session.test_table_name
            cursor = connection.cursor() 
            try:
                cursor.execute(f""" INSERT INTO {test_table_name} (heading, description, start_time, end_time, no_of_questions) VALUES (%s, %s, %s, %s, %s) """, [heading, description, start_time, end_time, no_of_questions])

                test_id = cursor.lastrowid

                num_questions = form.cleaned_data['no_of_questions']
                # query = (f""" INSERT INTO {session.test_questions_table_name} (test_id, question_id, marks) SELECT {test_id}, id, 1 FROM {session.subject.subjects_question_table_name} ORDER BY RANDOM() LIMIT {no_of_questions}; """)
                # print(query)
                cursor.execute(f"""
                    INSERT INTO {session.test_questions_table_name} (test_id, question_id, marks)
                    SELECT %s, id, 1 FROM {session.subject.subjects_question_table_name}
                    ORDER BY RANDOM() LIMIT %s;
                """, [test_id, no_of_questions])
                return redirect('teacher_test_edit_questions', session_id=session_id, test_id=test_id)  
            except Exception as e:
                messages.error(request, f'Error creating test: {e}')
    else:
        form = TestCreationForm(initial={'subject_question_table_name': session.subject.subjects_question_table_name})

    return render(request, 'teacher/test_create.html', {'is_teacher':True, 'user':request.user,'form': form})

@login_required
def test_edit(request, session_id, test_id):
    if request.user.is_teacher == -1:
        return render(request, 'base/404.html') 

    session = get_object_or_404(ClassSession, id=session_id)
    test_table_name = session.test_table_name
    # Fetch test data from the database using SQL queries
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {test_table_name} WHERE id = {test_id}")
        row = cursor.fetchone()
        if row:
            test_data = {
                'heading': row[1],
                'description': row[2],
                'start_time': row[3],
                'end_time': row[4],
                'no_of_questions': row[5],
                'subject_question_table_name': session.subject.subjects_question_table_name
            }
            # print(test_data)
            if request.method == 'POST':
                form = TestCreationForm(request.POST,initial={'subject_question_table_name': session.subject.subjects_question_table_name})
                if form.is_valid():
                    # Update test data in the database
                    update_query = f"""
                        UPDATE {test_table_name} 
                        SET heading = %s, description = %s, start_time = %s, end_time = %s, no_of_questions = %s
                        WHERE id = %s
                    """
                    cursor.execute(update_query, [
                        form.cleaned_data['heading'],
                        form.cleaned_data['description'],
                        form.cleaned_data['start_time'],
                        form.cleaned_data['end_time'],
                        form.cleaned_data['no_of_questions'],
                        test_id
                    ])
                    cursor = connection.cursor()
                    cursor.execute(f"SELECT * FROM {session.test_questions_table_name} WHERE test_id = {test_id}")
                    rows = cursor.fetchall()

                    row_count = len(rows)
                    # print(row_count , form.cleaned_data['no_of_questions'])

                    # print(row_count - form.cleaned_data['no_of_questions'])
                    if row_count > form.cleaned_data['no_of_questions']  :
                        excess_questions_count = row_count - form.cleaned_data['no_of_questions']
                        # print("excess_questions_count: ",excess_questions_count)
                        cursor.execute(f"DELETE FROM {session.test_questions_table_name} WHERE test_id = {test_id} ORDER BY RANDOM() LIMIT {excess_questions_count}")

                    elif row_count < form.cleaned_data['no_of_questions']:
                        additional_questions_count = abs(test_data['no_of_questions'] - form.cleaned_data['no_of_questions'] )
                        print("additional_questions_count: ",additional_questions_count)
    
                        cursor.execute(f"""INSERT INTO {session.test_questions_table_name} (test_id, question_id, marks)
                        SELECT {test_id}, sq.id, 1
                        FROM {session.subject.subjects_question_table_name} AS sq
                        LEFT JOIN {session.test_questions_table_name} AS tq 
                            ON sq.id = tq.question_id AND tq.test_id = {test_id}
                        WHERE tq.question_id IS NULL
                        ORDER BY RANDOM()
                        LIMIT {additional_questions_count}""")


                    return redirect('teacher_test_edit_questions', session_id=session_id, test_id=test_id) 
            else:
                form = TestCreationForm(initial=test_data)
            return render(request, 'teacher/test_edit.html', {'is_teacher': True, 'user': request.user, 'form': form,'session_id':session_id, 'test_id': test_id})
        else: 
            return HttpResponse("Test not found", status=404)

@login_required
def test_delete(request, session_id, test_id):
    if request.user.is_teacher == -1:
        return render(request, 'base/404.html') 

    session = get_object_or_404(ClassSession, id=session_id)
    test_table_name = session.test_table_name
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {session.test_questions_table_name} WHERE test_id = {test_id}")
        
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {session.response_table_name} WHERE test_id = {test_id}")

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {session.result_table_name} WHERE test_id = {test_id}")

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {session.test_table_name} WHERE id = {test_id}")
 
        return redirect('teacher_session_tests', session_id=session_id)   
    else:
        return render(request, 'teacher/test_delete.html', {'is_teacher': True, 'user': request.user, 'test_id': test_id})

@login_required
def test_edit_questions(request, session_id, test_id):
    if request.user.is_teacher == -1:
        return render(request, 'base/404.html') 

    session = get_object_or_404(ClassSession, id=session_id)
    test_table_name = session.test_table_name
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_question':
            # Delete the question from test_questions_table_name
            question_id = request.POST.get('question_id')
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {session.test_questions_table_name} WHERE test_id = {test_id} AND question_id = {question_id}")
            # Decrement the count of questions in test_table_name
            with connection.cursor() as cursor:
                cursor.execute(f"UPDATE {session.test_table_name} SET no_of_questions = no_of_questions - 1 WHERE id = {test_id}")
            messages.success(request, 'Question deleted successfully.')
            return redirect('teacher_test_edit_questions', session_id=session_id, test_id=test_id)
        elif action == 'get_random_question':
            # Check if there are available questions in subject
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {session.subject.subjects_question_table_name}")
                row = cursor.fetchone()
                total_questions = row[0] if row else 0
            # Check if test_questions_table_name already contains all questions from the subject
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {session.test_questions_table_name} WHERE test_id = {test_id}")
                row = cursor.fetchone()
                questions_in_test = row[0] if row else 0
            if questions_in_test >= total_questions:
                messages.warning(request, 'Add questions in subject to increase more.')
            else:
                # Get a random question from subjects_question_table_name that is not already in the test
                with connection.cursor() as cursor:
                    cursor.execute(f"""INSERT INTO {session.test_questions_table_name} (test_id, question_id, marks) 
                        SELECT {test_id}, sq.id, 1
                        FROM {session.subject.subjects_question_table_name} AS sq
                        LEFT JOIN {session.test_questions_table_name} AS tq 
                            ON sq.id = tq.question_id AND tq.test_id = {test_id}
                        WHERE tq.question_id IS NULL
                        ORDER BY RANDOM()
                        LIMIT 1""") 
                    random_question = cursor.fetchone() 
                    cursor.execute(f"UPDATE {session.test_table_name} SET no_of_questions = no_of_questions + 1 WHERE id = {test_id}")
            return redirect('teacher_test_edit_questions',session_id=session_id, test_id=test_id)
    else:
        # Fetch questions associated with the test
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT 
        tq.question_id, sq.author, sq.question, 
        qi.image AS question_image, 
        sq.option1, oi1.image AS option1_image, 
        sq.option2, oi2.image AS option2_image, 
        sq.option3, oi3.image AS option3_image, 
        sq.option4, oi4.image AS option4_image, 
        sq.correct_option, sq.explanation, 
        ei.image AS explanation_image, 
        tq.marks 
    FROM 
        {session.test_questions_table_name} AS tq 
    JOIN 
        {session.subject.subjects_question_table_name} AS sq 
    ON 
        tq.question_id = sq.id 
    LEFT JOIN 
        administration_uploadedimage AS qi ON sq.question_image = qi.id 
    LEFT JOIN 
        administration_uploadedimage AS oi1 ON sq.option1_image = oi1.id 
    LEFT JOIN 
        administration_uploadedimage AS oi2 ON sq.option2_image = oi2.id 
    LEFT JOIN 
        administration_uploadedimage AS oi3 ON sq.option3_image = oi3.id 
    LEFT JOIN 
        administration_uploadedimage AS oi4 ON sq.option4_image = oi4.id 
    LEFT JOIN 
        administration_uploadedimage AS ei ON sq.explanation_image = ei.id 
    WHERE 
        tq.test_id = {test_id}""")
            questions = cursor.fetchall()
        return render(request, 'teacher/test_edit_questions.html', {'is_teacher': True, 'user': request.user,'test_id': test_id, 'questions': questions})
    
