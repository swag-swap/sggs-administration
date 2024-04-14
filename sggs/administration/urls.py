from django.urls import path, include
from . import views 

urlpatterns = [ 
    path('notifications/', views.notification_list, name='notification_list'),
    path('approve_notification/', views.approve_notification, name='approve_notification'),path('register/', views.register, name='register'),
    path('get_otp/', views.get_otp, name='get_otp'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('edit-student-detail/', views.edit_student_detail, name='edit_student_detail'),
    path('edit-teacher-detail/', views.edit_teacher_detail, name='edit_teacher_detail'),
    path('edit-administrator-detail/', views.edit_administrator_detail, name='edit_administrator_detail'), 
    path('teacher/', include("teacher.urls"), name="teacher"),
    path('student/', include("student.urls"), name="student"), 

    path('home/', views.home, name='admin_home'),
    # path('edit/profile/', views.edit_profile, name='admin_edit_profile'),
    # path('notify/teacher/', views.notify_teacher, name='admin_notify_teacher'),
    # path('notify/student/', views.notify_student, name='admin_notify_student'),
    # path('add/teacher/', views.add_teacher, name='admin_add_teacher'),
    path('subject/add/', views.subject_add, name='admin_subject_add'),
    path('subject-list/',views.subject_list, name='admin_subject_list'),
    path('subject/edit/<int:subject_id>/', views.subject_edit, name='admin_subject_edit'), 
    path('subject/delete/<int:subject_id>/', views.subject_delete, name='admin_subject_delete'), 


    path('student/manage/', views.manage_student, name='admin_student_manage'),
    path('student/manage/<int:id>/', views.manage_student_detail, name='admin_student_manage_detail'),



    path('department/add/', views.department_add, name='admin_department_add'),
    path('department-list/',views.department_list, name='admin_department_list'),
    path('department/edit/<int:department_id>/', views.department_edit, name='admin_department_edit'), 
    path('department/delete/<int:department_id>/', views.department_delete, name='admin_department_delete'), 

    path('session/add/', views.session_add, name='admin_add_session'),
    path('session-list/',views.session_list, name='admin_session_list'),
    path('session/edit/<int:session_id>/', views.session_edit, name='admin_edit_session'), 
    path('session/delete/<int:session_id>/', views.session_delete, name='admin_delete_session'), 
    path('session/<int:session_id>/attendance/', views.session_attendance, name='session_attendance'),


    path('teacher/manage/', views.manage_teacher, name='admin_manage_teacher'),
    path('teacher/details/<int:teacher_id>/', views.teacher_details, name='admin_teacher_detail'),


    # path('view/notifications/', views.view_notifications, name='teacher_view_notifications'),
    # path('feedback/', views.feedback, name='teacher_feedback'), 
    # path('view/attendence/', views.view_attendence, name='admin_view_attendence'),

]
