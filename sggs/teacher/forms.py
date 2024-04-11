from django import forms
from administration.models import Teacher, Department

class TeacherDetailsForm(forms.ModelForm):
    department = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Teacher
        fields = [] 