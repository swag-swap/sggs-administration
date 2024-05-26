from django import forms
from .models import Student, Department, Semester, Fee, CustomUser, OTP, Teacher, Administrator, ClassSession, Subject

class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'), 
    ]
    role = forms.MultipleChoiceField(label='Role', choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple)
    otp = forms.CharField(label='OTP', max_length=6)
    

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})  

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

# Students form
class StudentForm(forms.ModelForm):  
    year_1_fee = forms.DecimalField(label='Year 1 Fee')
    year_2_fee = forms.DecimalField(label='Year 2 Fee')
    year_3_fee = forms.DecimalField(label='Year 3 Fee')
    year_4_fee = forms.DecimalField(label='Year 4 Fee')

    class Meta:
        model = Student
        fields = ['department', 'semester', 'roll_number', 'date_of_birth', 'address', 'contact_number']

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists. Please choose a different one.')
        return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                fee = Fee.objects.get(student=self.instance)
                self.fields['year_1_fee'].initial = fee.year_1_fee
                self.fields['year_2_fee'].initial = fee.year_2_fee
                self.fields['year_3_fee'].initial = fee.year_3_fee
                self.fields['year_4_fee'].initial = fee.year_4_fee
            except Fee.DoesNotExist:
                pass

    def save(self):
        student = super().save()
        student.save()
        print('HI1') 
        try:
            print('try block')
            fee = Fee.objects.get(student=student) 
            fee.year_1_fee = self.cleaned_data['year_1_fee']
            fee.year_2_fee = self.cleaned_data['year_2_fee']
            fee.year_3_fee = self.cleaned_data['year_3_fee']
            fee.year_4_fee = self.cleaned_data['year_4_fee']
            fee.save()
        except Fee.DoesNotExist:
            print('except block')
            Fee.objects.create(
                student=student,
                year_1_fee=self.cleaned_data['year_1_fee'],
                year_2_fee=self.cleaned_data['year_2_fee'],
                year_3_fee=self.cleaned_data['year_3_fee'],
                year_4_fee=self.cleaned_data['year_4_fee']
            )
        return student

class StudentSearchForm(forms.Form):
    reg_no = forms.CharField(label='Student Registration Number', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter registration number'}))

class RejectionForm(forms.Form):
    rejection_message = forms.CharField(label='Rejection Message', widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}))



# Teachers form 
    
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['departments', 'subjects']


# Administrators form
        
class AdministratorForm(forms.ModelForm):
    class Meta:
        model = Administrator
        fields = ['departments']

class ClassSessionForm(forms.ModelForm): 
    # teacher = forms.ModelMultipleChoiceField(
    #     label='Teacher', 
    #     queryset=Teacher.objects.all(),   
    #     widget=forms.CheckboxSelectMultiple()
    # )
    class Meta:
        model = ClassSession
        fields = ['department', 'semester', 'subject',  'year', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
         
            
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter subject'}) 
        self.fields['semester'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter semester'})
        self.fields['department'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter department'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'}) 
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})  
        self.fields['year'].widget.attrs.update({'class': 'form-control'}) 
 

class EditClassSessionForm(forms.ModelForm): 
    teacher = forms.ModelMultipleChoiceField(
        label='Teacher', 
        queryset=Teacher.objects.all(),   
        widget=forms.CheckboxSelectMultiple()
    )
    class Meta:
        model = ClassSession
        fields = ['teacher','students', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'}) 
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})   



class SessionFilterForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        labels = {
            'name': 'Subject Name',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject name'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        labels = {
            'name': 'Department Name',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department name'}),
        }

