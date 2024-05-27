from django.urls import path, include
from . import views 

urlpatterns = [ 
    path('', views.home, name='student_home'),
    path('sessions/', views.sessions, name='student_sessions'),
    path('session/<int:session_id>/', views.session_detail, name='student_session_detail'),
    path('session/<int:session_id>/test/<int:test_id>/', views.give_test, name='student_test'),
    path('session/<int:session_id>/test/<int:test_id>/detail/', views.test_detail, name='student_test_detail'),
    path('session/<int:session_id>/test/<int:test_id>/result/', views.test_result, name='student_test_result'),
    path('session/<int:session_id>/test/<int:test_id>/response/', views.submit_test_response, name='submit_test_response'),
    # path('edit/profile/', views.edit_profile, name='student_edit_profile'),
    # path('view/attendence/', views.view_attendence, name='student_view_attendence'),
    path('view/notifications/', views.view_notifications, name='student_view_notifications'),
    # path('feedback/', views.feedback, name='student_feedback'), 
    path('mark/attendence/<int:session_id>', views.mark_attendance, name='student_mark_attendence'),
]
