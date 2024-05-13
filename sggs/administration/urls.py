from django.urls import path, include
from .views import * 

urlpatterns = [ 
    path('notifications/', notifications, name='notifications'),
    path('approve_notification/', approve_notification, name='admin_approve_notification'), 

    path('', home, name='admin_home'),
    # path('edit/profile/', views.edit_profile, name='admin_edit_profile'),
    # path('notify/teacher/', views.notify_teacher, name='admin_notify_teacher'),
    # path('notify/student/', views.notify_student, name='admin_notify_student'),
    # path('add/teacher/', views.add_teacher, name='admin_add_teacher'),
    path('subject/add/', subject_add, name='admin_subject_add'),
    path('subject-list/',subject_list, name='admin_subject_list'),
    path('subject/edit/<int:subject_id>/', subject_edit, name='admin_subject_edit'), 
    path('subject/delete/<int:subject_id>/', subject_delete, name='admin_subject_delete'), 


    path('manage/student/', manage_student, name='admin_student_manage'),
    path('manage/student/<int:id>/', manage_student_detail, name='admin_student_manage_detail'),
    path('student/add/', add_student, name='admin_student_add'),
    path('student/add/excel/', add_student_from_excel, name='admin_student_add_excel'),
    path('approve_student_profile/<int:user_id>/', approve_student_profile, name='approve_student_profile'),



    path('department/add/', department_add, name='admin_department_add'),
    path('department-list/',department_list, name='admin_department_list'),
    path('department/edit/<int:department_id>/', department_edit, name='admin_department_edit'), 
    path('department/delete/<int:department_id>/', department_delete, name='admin_department_delete'), 

    path('session/add/', session_add, name='admin_add_session'),
    path('session-list/',session_list, name='admin_session_list'),
    path('session/edit/<int:session_id>/', session_edit, name='admin_edit_session'), 
    path('session/delete/<int:session_id>/', session_delete, name='admin_delete_session'), 
    path('session/<int:session_id>/attendance/', session_attendance, name='session_attendance'),


    path('manage/teacher/', manage_teacher, name='admin_manage_teacher'),
    path('detail/teacher/<int:teacher_id>/', teacher_details, name='admin_teacher_detail'),
    path('teacher/add/excel/', add_teacher_from_excel, name='admin_teacher_add_excel'),
    path('teacher/add/', add_teacher, name='admin_teacher_add'),
    path('approve_teacher_profile/<int:user_id>/', approve_teacher_profile, name='approve_teacher_profile'),


    path('approve_administration_profile/<int:user_id>/', approve_administration_profile, name='approve_administration_profile'),
    path('admin/add/excel/', add_admin_from_excel, name='admin_admin_add_excel'),

    path('approve_librarian_profile/<int:user_id>/', approve_librarian_profile, name='approve_librarian_profile'),


    # path('view/notifications/', views.view_notifications, name='admin_view_notifications'),
    # path('view/messages/', views.view_messages, name='admin_view_messages'),
    # path('feedback/', views.feedback, name='teacher_feedback'),  

]
