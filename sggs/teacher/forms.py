from django import forms
from administration.models import Teacher, Department, Subject
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

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
    question_image_path = forms.ImageField(label='Question Image Path', required=False)
    option1 = forms.CharField(label='Option 1', widget=forms.Textarea)
    option1_image_path = forms.ImageField(label='Option 1 Image Path', required=False)
    option2 = forms.CharField(label='Option 2', widget=forms.Textarea)
    option2_image_path = forms.ImageField(label='Option 2 Image Path', required=False)
    option3 = forms.CharField(label='Option 3', widget=forms.Textarea)
    option3_image_path = forms.ImageField(label='Option 3 Image Path', required=False)
    option4 = forms.CharField(label='Option 4', widget=forms.Textarea)
    option4_image_path = forms.ImageField(label='Option 4 Image Path', required=False)
    correct_option = forms.IntegerField(label='Correct Option')
    explanation = forms.CharField(label='Explanation', widget=forms.Textarea)
    explanation_image_path = forms.ImageField(label='Explanation Image Path', required=False)

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))


class ImageUploadForm(forms.Form):
    image = forms.ImageField()