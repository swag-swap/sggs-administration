from django import forms
from administration.models import Student, Department, Semester, Fee, CustomUser, OTP, Teacher, Administrator, ClassSession, Subject

class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'), 
    ]
    role = forms.MultipleChoiceField(label='Role', choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple())
    otp = forms.CharField(label='OTP', max_length=6, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

# Students form
class StudentForm(forms.ModelForm):    
    year_1_fee = forms.DecimalField(label='Year 1 Fee', widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_2_fee = forms.DecimalField(label='Year 2 Fee', widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_3_fee = forms.DecimalField(label='Year 3 Fee', widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_4_fee = forms.DecimalField(label='Year 4 Fee', widget=forms.TextInput(attrs={'class': 'form-control'}))


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
        for field_name, field in self.fields.items(): 
            field.widget.attrs.update({'class': 'form-control'})
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


# Teachers form 
    
class TeacherForm(forms.ModelForm): 
    departments = forms.ModelMultipleChoiceField(
        label='Departments', 
        queryset=Department.objects.all(),   
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Teacher
        fields = ['departments']


# Administrators form
        
class AdministratorForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        label='Departments', 
        queryset=Department.objects.all(),   
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Administrator
        fields = ['departments']
