from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

class LoginForm(AuthenticationForm):
    pass
