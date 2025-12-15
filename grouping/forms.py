from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'coding', 'design', 'writing', 'presenting']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Name', 'style': 'padding: 5px; width: 150px;'}),
            'coding': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'width: 50px;'}),
            'design': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'width: 50px;'}),
            'writing': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'width: 50px;'}),
            'presenting': forms.NumberInput(attrs={'min': 1, 'max': 5, 'style': 'width: 50px;'}),
        }