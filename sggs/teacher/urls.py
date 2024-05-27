from django.urls import path, include
from . import views 

urlpatterns = [ 
    path('', views.teacher_home, name='teacher_home'),
    path('edit/profile/', views.edit_profile, name='teacher_edit_profile'),
    path('sessions/', views.teacher_sessions, name='teacher_sessions'),
    path('session/<int:session_id>/attendance/', views.session_attendance, name='teacher_session_attendance'),
    path('session/<int:session_id>/start-attendance/', views.start_attendence, name='start_attendence'),
    path('session/<int:session_id>/stop-attendance/', views.stop_attendence, name='stop_attendence'),
    path('session/<int:session_id>/take/attendence/', views.take_attendance, name='teacher_take_attendence'),

    # Subjects
    path('subject/<int:subject_id>/add_question/', views.add_question, name='teacher_add_question'),
    path('subject/<int:subject_id>/questions/excel/', views.subject_questions_from_excel, name='teacher_subject_questions_from_excel'),
    path('subject/<int:subject_id>/questions/', views.subject_questions, name='teacher_subject_questions'),
    path('subjects/', views.subject_list, name='teacher_subject_list'),
    path('question/delete/<int:subject_id>/<int:question_id>/', views.teacher_delete_question, name='teacher_delete_question'),

    ## Test
    path('session/<int:session_id>/tests/', views.session_tests, name='teacher_session_tests'),
    path('session/<int:session_id>/test/create/', views.test_create, name='teacher_test_create'),
    path('session/<int:session_id>/test/<int:test_id>/edit/', views.test_edit, name='teacher_test_edit'),
    path('session/<int:session_id>/test/<int:test_id>/edit/questions/', views.test_edit_questions, name='teacher_test_edit_questions'),
    path('session/<int:session_id>/test/<int:test_id>/delete', views.test_delete, name='teacher_test_delete'),
    path('session/<int:session_id>/test/<int:test_id>/result/', views.test_result, name='teacher_test_result'),
    path('session/<int:session_id>/test/<int:test_id>/activity/', views.test_activity_dashboard, name='teacher_test_activity_dashboard'),

    # path('notify/', views.notify, name='teacher_notify'),
    # path('feedback/', views.feedback, name='teacher_feedback'), 

]
