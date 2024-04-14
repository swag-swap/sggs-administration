from django.shortcuts import render, redirect
from .forms import TeacherDetailsForm
from administration.models import Teacher, Notification
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def edit_profile(request):
    if request.user.is_teacher != -1:
        teacher = Teacher.objects.get(user=request.user)
        if request.method == 'POST':
            form = TeacherDetailsForm(request.POST, instance=teacher)
            if form.is_valid():
                form.instance.user = request.user
                teacher = form.save()
                existing_notification = Notification.objects.filter( 
                    notification_type=1
                ).exists()

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
        return render(request, 'teacher/edit_profile.html', {'form': form})
    else:
        render(request, 'base/404.html')

