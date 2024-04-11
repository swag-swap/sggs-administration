from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime
from administration.models import Student

def mark_attendance(request):
    if request.user.is_student == 1:
        if request.method == 'POST':
            student_id = Student.objects.get(user=request.user).id
            date = request.POST.get('date') 
            is_present = request.POST.get('is_present')

            # Insert attendance record using raw SQL query
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO z_2024_cse_Semester_1_OS_attendence (student_id, date, is_present) VALUES (%s, %s, %s)",
                            [student_id, date, is_present])

            return redirect('admin_home')  # Redirect to a success page

        return render(request, 'student/mark_attendance.html',{'is_student': True, 'user': request.user})
    else:
        return render(request, 'base/404.html')


def attendance_success(request):
    return render(request, 'attendance_success.html')