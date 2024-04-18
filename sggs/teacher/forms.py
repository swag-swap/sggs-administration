from django import forms
from administration.models import Teacher, Department, Subject
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django.utils import timezone
from django.db import connection

class TeacherDetailsForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departments'].widget = forms.CheckboxSelectMultiple()
        self.fields['departments'].queryset = Department.objects.all()
        self.fields['subjects'].widget = forms.CheckboxSelectMultiple()
        self.fields['subjects'].queryset = Subject.objects.all()

    class Meta:
        model = Teacher
        fields = ['departments', 'subjects'] 
 
class AttendanceExtractionForm(forms.Form):
    image = forms.ImageField()

class QuestionForm(forms.Form):
    question = forms.CharField(label='Question', widget=forms.Textarea)
    question_image = forms.ImageField(label='Question Image', required=False)
    option1 = forms.CharField(label='Option 1', widget=forms.Textarea)
    option1_image = forms.ImageField(label='Option 1 Image', required=False)
    option2 = forms.CharField(label='Option 2', widget=forms.Textarea)
    option2_image = forms.ImageField(label='Option 2 Image', required=False)
    option3 = forms.CharField(label='Option 3', widget=forms.Textarea)
    option3_image = forms.ImageField(label='Option 3 Image', required=False)
    option4 = forms.CharField(label='Option 4', widget=forms.Textarea)
    option4_image = forms.ImageField(label='Option 4 Image', required=False)
    correct_option = forms.IntegerField(label='Correct Option')
    explanation = forms.CharField(label='Explanation', widget=forms.Textarea)
    explanation_image = forms.ImageField(label='Explanation Image', required=False)

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class TestCreationForm(forms.Form):
    heading = forms.CharField(label='Heading', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'class': 'form-control'}))
    start_time = forms.DateTimeField(label='Start Time', initial=timezone.now(), widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))
    end_time = forms.DateTimeField(label='End Time', initial=timezone.now(), widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))

    def __init__(self, *args, **kwargs):
        super(TestCreationForm, self).__init__(*args, **kwargs)
        max_questions = self.get_max_questions()
        self.fields['no_of_questions'] = forms.IntegerField(label='Number of Questions', min_value=1, max_value=max_questions, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def get_max_questions(self):
        subject_question_table_name = self.initial.get('subject_question_table_name', '')
        if subject_question_table_name:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {subject_question_table_name}")
                row = cursor.fetchone()
                if row:
                    return row[0]
        return 0
    
