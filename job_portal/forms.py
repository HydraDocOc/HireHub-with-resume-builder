from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Company, Job

class UserLoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[('user', 'User'), ('admin', 'Admin')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'role']

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'mobile', 'password', 'confirm_password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'logo_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'location', 'salary_range', 'job_type', 'requirements']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
        }

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'location', 'salary_range', 'job_type', 'requirements']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'id': 'description'}),
            'requirements': forms.Textarea(attrs={'rows': 3, 'id': 'requirements'}),
            'title': forms.TextInput(attrs={'id': 'title'}),
            'location': forms.TextInput(attrs={'id': 'location'}),
            'salary_range': forms.TextInput(attrs={'id': 'salary', 'placeholder': 'e.g. ₹80,000 - ₹1,00,000'}),
            'job_type': forms.Select(attrs={'id': 'jobType'}, choices=[
                ('Full-time', 'Full-time'),
                ('Part-time', 'Part-time'),
                ('Contract', 'Contract'),
                ('Remote', 'Remote'),
            ])
        }

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Job title or keyword',
        'class': 'form-control'
    }))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Location',
        'class': 'form-control'
    }))
