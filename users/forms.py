from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Permission, Group
from django import forms
from events.forms import StyledFormMixin
import re


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class CustomRegistrationForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        errors = []
        if len(password1)<8:
            errors.append('password must be at least 8 characters')
        if not re.search(r'[A-Z]', password1):
            errors.append('Must include an uppercase letter')
        if not re.search(r'[a-z]', password1):
            errors.append('Must include a lowercase letter')
        if not re.search(r'[0-9]', password1):
            errors.append('Must include a number')
        if not re.search(r'[@#$%^&+=]', password1):
            errors.append('Must include a special character')
        if errors:
            raise forms.ValidationError(errors)
        return password1
    def clean(self):
        clean_data = super().clean()
        p1 = clean_data.get('password1')
        p2 = clean_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return clean_data
    
class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AssignRoleForm(StyledFormMixin, forms.Form):
    role = forms.ModelChoiceField(queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple,required=False,label="Assign Permission")

    class Meta:
        model = Group
        feilds = ['name', 'permissions']

class CreateGroupForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']