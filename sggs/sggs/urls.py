from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tables/', admin.site.urls),

    # Main endpoints
    path('admin/', include("administration.urls"), name="administration"),
    path('teacher/', include("teacher.urls"), name="teacher"),
    path('student/', include("student.urls"), name="student"),
    path('library/', include("library.urls"), name="library"),

    #  
    path('register/', views.register, name='register'),
    path('get_otp/', views.get_otp, name='get_otp'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('edit-student-detail/', views.edit_student_detail, name='edit_student_detail'),
    path('edit-teacher-detail/', views.edit_teacher_detail, name='edit_teacher_detail'),
    path('edit-administrator-detail/', views.edit_administrator_detail, name='edit_administrator_detail'), 
    path('edit-librarian-detail/', views.edit_librarian_detail, name='edit_librarian_detail'), 
]
 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 