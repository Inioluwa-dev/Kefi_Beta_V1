from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as DjangoPasswordResetForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control auth-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control auth-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control auth-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control auth-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = ''
            field.widget.attrs['class'] += ' form-control auth-input'

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control auth-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control auth-input'}))

class CustomPasswordResetForm(DjangoPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control auth-input'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic', 'cover_image', 'location', 'links', 'is_private']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ' '}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'links': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add links (one per line, e.g. https://yourwebsite.com)'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add floating label support and consistent classes
        self.fields['bio'].widget.attrs.setdefault('placeholder', ' ')
        self.fields['location'].widget.attrs.setdefault('placeholder', ' ')
        self.fields['links'].widget.attrs.setdefault('placeholder', 'Add links (one per line, e.g. https://yourwebsite.com)')
        # File fields: add class for styling
        self.fields['profile_pic'].widget.attrs['class'] = 'form-control-file'
        self.fields['cover_image'].widget.attrs['class'] = 'form-control-file'
        # Checkbox: ensure class for switch styling
        self.fields['is_private'].widget.attrs['class'] = 'form-check-input'
