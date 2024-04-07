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

    # path('home/', views.home, name='admin_home'),
    # path('edit/profile/', views.edit_profile, name='admin_edit_profile'),
    # path('view/attendence/', views.view_attendence, name='admin_view_attendence'),
    # path('notify/teacher/', views.notify_teacher, name='admin_notify_teacher'),
    # path('notify/student/', views.notify_student, name='admin_notify_student'),
    # path('add/teacher/', views.add_teacher, name='admin_add_teacher'),
    # path('manage/teacher/', views.manage_teacher, name='admin_manage_teacher'),
    # path('add/subject/', views.add_subject, name='admin_add_subject'),
    # path('manage/subject/', views.manage_subject, name='admin_manage_subject'),
    # path('add/session/', views.add_session, name='admin_add_session'),
    # path('manage/session/', views.manage_session, name='admin_manage_session'), 
    # path('view/notifications/', views.view_notifications, name='teacher_view_notifications'),
    # path('feedback/', views.feedback, name='teacher_feedback'), 

]
