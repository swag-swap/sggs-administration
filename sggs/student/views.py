from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from datetime import datetime, date
from django.http import JsonResponse
from django.utils import timezone
from administration.models import Student, ClassSession, Notification
from django.contrib.auth.decorators import login_required
import random, json 

@login_required
def validate(request):
    if request.user.is_student < 1:
        return False
    return True
    
@login_required
def home(request):
    if not validate(request):
        return render(request, 'base/404.html')
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student = Student.objects.get(id=student_id)
     
    class_sessions = ClassSession.objects.filter(students=student)
    # Attendance of all the sessions
    attendance_data = {}
    for session in class_sessions:
        print(session.attendence_table_name)
        total_active_days = session.total_active_days
        query = f"""
            SELECT COUNT(*)
            FROM {session.attendence_table_name}
            WHERE student_id = {student_id}
            AND is_present = TRUE
        """
        cursor = connection.cursor()
        cursor.execute(query) 
        attendance_count = cursor.fetchone()[0]
        print(f"Attendance count for {session.attendence_table_name}: {attendance_count}")
        if total_active_days != 0:
            attendance_percentage = (attendance_count / total_active_days) * 100
        else:
            attendance_percentage = 0
        
        attendance_data[session.subject.name] = {
            'attendance_count': attendance_count,
            'total_active_days': total_active_days,
            'attendance_percentage': attendance_percentage
        }
      
    context = {
        'attendance_data': attendance_data,
        'is_student': True, 
        'user': request.user
    }
    
    return render(request, 'student/home.html', context)

@login_required
def sessions(request):
    if not validate(request):
        return render(request, 'base/404.html') 
    student_id = request.user.student_profile.id
    student = Student.objects.get(id=student_id)
    
    sessions = ClassSession.objects.filter(students=student)
    today = date.today().strftime('%Y-%m-%d')
    # print(today)
    session_info = []

    for session in sessions:
        attendance_table_name = session.attendence_table_name
        if session.attendence_active:
            attendance_status = True
        else :
            attendance_status = False
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {attendance_table_name} WHERE student_id = {student_id} AND date = '{today}'")
        row_count = cursor.fetchone()[0]
        if row_count !=0:
            cursor.execute(f"SELECT is_present FROM {attendance_table_name} WHERE student_id = {student_id} AND date = '{today}'")
            attendance_data = cursor.fetchone()[0]
        else:
            attendance_data = -1
        # print(attendance_data, attendance_status, row_count)

        session_info.append({
            "session": session,
            "attendance_status": attendance_status,
            "attendance_data":attendance_data,
            "row_count": row_count,
        }) 
    # print(session_info)
    
    context = {
        'session_info': session_info,
        'is_student': True, 
        'user': request.user
    }
    return render(request, 'student/sessions.html', context)

def session_detail(request, session_id):
    if not validate(request):
        return render(request, 'base/404.html')
    
    # Retrieve the specific session
    session = get_object_or_404(ClassSession, id=session_id)
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student_profile = request.user.student_profile
 
    if not student_profile in session.students.all():
        return render(request, 'base/404.html')
    
    # Attendence
    total_active_days = session.total_active_days
    query = f"""
        SELECT COUNT(*)
        FROM {session.attendence_table_name}
        WHERE student_id = {student_id}
        AND is_present = TRUE
    """
    cursor = connection.cursor()
    cursor.execute(query) 
    attendance_count = cursor.fetchone()[0]
    print(f"Attendance count for {session.attendence_table_name}: {attendance_count}")
    if total_active_days != 0:
        attendance_percentage = (attendance_count / total_active_days) * 100
    else:
        attendance_percentage = 0
    

    # Tests
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT id, heading, description, start_time, end_time, no_of_questions
            FROM {session.test_table_name}
        """)
        tests = cursor.fetchall()

    current_time = timezone.now()
    active_tests = []
    previous_tests = []

    for test in tests:
        if test[4] < current_time:
            previous_tests.append(test)
        else:
            active_tests.append(test)


    context = {
        'attendance_count': attendance_count,
        'attendance_percentage': attendance_percentage,
        'total_active_days': total_active_days,
        'session': session,
        'active_tests': active_tests,
        'previous_tests': previous_tests,
        'is_student': True, 
        'user': request.user
    }
    return render(request, 'student/session_detail.html', context)

def test_detail(request, session_id, test_id):
    if not validate(request):
        return render(request, 'base/404.html')
    
    # Retrieve the specific session
    session = get_object_or_404(ClassSession, id=session_id)
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student_profile = request.user.student_profile
 
    if not student_profile in session.students.all():
        return render(request, 'base/404.html')
 
     
    query = f"""
        SELECT *
        FROM {session.test_table_name}
        WHERE id = {test_id}
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        test_details = cursor.fetchone()
 
    if test_details:
        test_id, heading, description, start_time, end_time, no_of_questions = test_details
 
        current_time = timezone.now()
 
        if start_time <= current_time < end_time: 
            attendance_query = f"""
                SELECT COUNT(*)
                FROM {session.result_table_name}
                WHERE test_id = {test_id} AND student_id = {student_id}
            """
            with connection.cursor() as cursor:
                cursor.execute(attendance_query)
                attendance_count = cursor.fetchone()[0]
 
                if attendance_count == 0:
                    take_test_button = True
                else:
                    take_test_button = False

                context = {
                    'heading': heading,
                    'description': description,
                    'start_time': start_time,
                    'end_time': end_time,
                    'no_of_questions': no_of_questions,
                    'take_test_button': take_test_button,
                    'session_id': session_id,
                    'test_id': test_id,
                    'test_details': True,
                    'is_student': True, 
                    'user': request.user
                }
                return render(request, 'student/test_detail.html', context)
        elif current_time > end_time:
            result_message = "Test has ended. Displaying results..."
            context = {
                'heading': heading,
                'description': description,
                'start_time': start_time,
                'end_time': end_time,
                'no_of_questions': no_of_questions,
                'result_message': result_message,
                'session_id': session_id,
                'test_id': test_id,
                'test_details': True,
                'is_student': True, 
                'user': request.user
            }
            return render(request, 'student/test_detail.html', context)
    else:
        return render(request, 'base/404.html')

def give_test(request, session_id, test_id):
    if not validate(request):
        return render(request, 'base/404.html')
    
    # Retrieve the specific session
    session = get_object_or_404(ClassSession, id=session_id)
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student_profile = request.user.student_profile
 
    if not student_profile in session.students.all():
        return render(request, 'base/404.html')

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {session.result_table_name} WHERE test_id = {test_id} AND student_id = {student_id}")
        row_count = cursor.fetchone()[0] 
    if row_count != 0:
        return JsonResponse({'message': 'You already submitted the test!'})

    if student_department != session.department or student_year != session.year:
        return render(request, 'base/404.html')
    
    ## Test details
    query = f"""
        SELECT heading, description, start_time, end_time, no_of_questions, id
        FROM {session.test_table_name}
        WHERE id = {test_id}
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        test_details = cursor.fetchone() 

    ## Test questions 
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT 
        tq.question_id, sq.author, sq.question, 
        qi.image AS question_image, 
        sq.option1, oi1.image AS option1_image, 
        sq.option2, oi2.image AS option2_image, 
        sq.option3, oi3.image AS option3_image, 
        sq.option4, oi4.image AS option4_image,  
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
    WHERE 
        tq.test_id = {test_id}""")
        questions = cursor.fetchall()
    # print(test_details, questions)
    
    random.shuffle(questions)
    
    context = {
        'test_details': test_details,
        'shuffled_questions': questions,
        'test_id': test_id,
        'session_id': session_id,
        'is_student': True, 
        'user': request.user
    }

    return render(request, 'student/give_test.html', context) 

def submit_test_response(request, session_id, test_id):
    if not validate(request):
        return render(request, 'base/404.html')
    
    session = get_object_or_404(ClassSession, id=session_id)
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student_profile = request.user.student_profile
 
    if not student_profile in session.students.all():
        return render(request, 'base/404.html')

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {session.result_table_name} WHERE test_id = {test_id} AND student_id = {student_id}")
        row_count = cursor.fetchone()[0] 
    if row_count != 0:
        return JsonResponse({'message': 'You already submitted the test!'})

    if request.method == 'POST':
        data = json.loads(request.body)
        
        selected_options = data.get('selected_options', []) 
        submission_time = data.get('submission_time')
        total_time_taken = data.get('total_time_taken')
        total_off_screen_time = data.get('total_off_screen_time')
        total_marks = 0
        mark_obtained = 0
        for selected_option in selected_options:
            question_id = selected_option['question_id']
            option = selected_option['selected_option']
            with connection.cursor() as cursor:
                # Getting the correct_option    
                cursor.execute(f"SELECT correct_option FROM {session.subject.subjects_question_table_name} WHERE id = {question_id}")
                correct_option = cursor.fetchone() 
                # Storing the response of student in response table 
                cursor.execute(f"INSERT INTO {session.response_table_name} (test_id, student_id, question_id, option_selected) VALUES ({test_id}, {student_id}, {question_id}, {option})")

            total_marks += 1
            print(question_id, option, correct_option[0])
            if int(option) == correct_option[0]:
                mark_obtained+=1
        print(mark_obtained, total_marks)
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO {session.result_table_name} (test_id, student_id, mark_obtained, total_marks, submission_time, total_time_taken, total_off_screen_time) VALUES ({test_id}, {student_id}, {mark_obtained}, {total_marks}, {submission_time}, {total_time_taken}, {total_off_screen_time})")
        return JsonResponse({'message': 'Test response submitted successfully'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def test_result(request, session_id, test_id):
    if not validate(request):
        return render(request, 'base/404.html')
    
    session = get_object_or_404(ClassSession, id=session_id)
    student_department = request.user.student_profile.department
    student_year = request.user.student_profile.year
    student_id = request.user.student_profile.id
    student_profile = request.user.student_profile
 
    if not student_profile in session.students.all():
        return render(request, 'base/404.html')


    # Retrieve the test details
    query_test_details = f"""
        SELECT heading, description, start_time, end_time, no_of_questions
        FROM {session.test_table_name}
        WHERE id = {test_id}
    """
    with connection.cursor() as cursor:
        cursor.execute(query_test_details)
        test_details = cursor.fetchone()

    # Retrieve the test result
    query_test_result = f"""
        SELECT mark_obtained, total_marks
        FROM {session.result_table_name}
        WHERE test_id = {test_id} AND student_id = {request.user.student_profile.id}
    """
    with connection.cursor() as cursor:
        cursor.execute(query_test_result)
        test_result = cursor.fetchone()

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
        tq.marks , rt.option_selected
    FROM 
        {session.test_questions_table_name} AS tq 

    JOIN 
        {session.response_table_name} as rt 
    ON 
        tq.question_id = rt.question_id AND rt.student_id = {student_id}

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

    if test_result:
        score = test_result[0]
        total_marks = test_result[1]
        percentage = (score / total_marks) * 100
    else:
        score = None
        percentage = None

    context = {
        'session': session,
        'test_details': test_details,
        'score': score,
        'percentage': percentage,
        'total_marks':total_marks,
        'questions': questions,
        'is_student': True, 
        'user': request.user,
    }

    return render(request, 'student/test_result.html', context)



def mark_attendance(request,session_id):
    if not validate(request):
        return render(request, 'base/404.html')  
    session = get_object_or_404(ClassSession, pk=session_id)
    if not session.attendence_active:
        return render(request, 'base/404.html') 
    student_id = Student.objects.get(user=request.user).id
    formatted_date = date.today().strftime('%Y-%m-%d')
    is_present = 1

    # Insert attendance record using raw SQL query
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT COUNT(*) FROM {session.attendence_table_name} WHERE student_id = {student_id} AND date = '{formatted_date}'""")
        row_count = cursor.fetchone()[0]

        if row_count == 0: 
            cursor.execute(f"""
                INSERT INTO {session.attendence_table_name} (student_id, date, is_present)
                VALUES ({student_id}, '{formatted_date}', {is_present})
            """) 
        else: 
            cursor.execute(f"""
                UPDATE {session.attendence_table_name}
                SET is_present = {is_present}
                WHERE student_id = {student_id} AND date = '{formatted_date}'
            """) 
    print(student_id, formatted_date, "dflkjalsdkf")
    return redirect('student_sessions')  

    # return redirect('student_sessions')


def attendance_success(request):
    if not validate(request):
        return render(request, 'base/404.html')
    return render(request, 'attendance_success.html')


@login_required
def view_notifications(request):
    if not validate(request):
        return render(request, 'base/404.html')
    
    notifications = Notification.objects.filter(
        to_user=request.user,
        for_student=True
    ).order_by('-created_at')
    
    notifications.update(read=True)

    context = {
        'user': request.user,
        'is_student': True,
        'notifications': notifications
    }
    
    return render(request, 'student/student_notifications.html', context)