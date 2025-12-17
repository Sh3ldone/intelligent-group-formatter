from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # <--- Missing import fixed
from .models import Student, Section

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter Class Name (e.g. BSCS-2A)', 
                'style': 'padding: 10px; width: 100%; border-radius: 4px; border: 1px solid #ccc; background-color: #2d2d2d; color: white;'
            }),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'coding', 'design', 'writing', 'presenting']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter Name', 
                'style': 'padding: 10px; width: 100%; border-radius: 4px; border: 1px solid #444; background: #2d2d2d; color: white;'
            }),
            'coding': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'padding: 5px; width: 60px; background: #2d2d2d; color: white; border: 1px solid #444;'}),
            'design': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'padding: 5px; width: 60px; background: #2d2d2d; color: white; border: 1px solid #444;'}),
            'writing': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'padding: 5px; width: 60px; background: #2d2d2d; color: white; border: 1px solid #444;'}),
            'presenting': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'padding: 5px; width: 60px; background: #2d2d2d; color: white; border: 1px solid #444;'}),
        }

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')