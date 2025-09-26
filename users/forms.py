from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Profile

class UserRegisterForm(UserCreationForm):
    # No backend email verification check; handled by frontend only
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control auth-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control auth-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control auth-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control auth-input'}),
        }


    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        return username.lower()

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

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        return username.lower()

class CustomPasswordResetForm(DjangoPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control auth-input'})
    
    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Override save method to use our custom HTML email template
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            # Ensure we don't use localhost in production
            if 'localhost' in domain or '127.0.0.1' in domain:
                domain = 'kefi.onrender.com'
        else:
            site_name = domain = domain_override
        
        email_field_name = User.get_email_field_name()
        for user in self.get_users(email):
            if not user.is_active:
                continue
            user_email = getattr(user, email_field_name)
            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                'uid': user.pk,
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            
            # Use our custom HTML email template
            html_content = render_to_string('emails/password_reset_email.html', context)
            
            subject = f"🔑 Reset Your Password - Kefi"
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=f"Click the link to reset your password: {context['protocol']}://{domain}{reverse('password_reset_confirm', kwargs={'uidb64': context['uid'], 'token': context['token']})}",
                from_email=from_email,
                to=[user_email],
            )
            
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'links', 'is_private']  # Exclude file fields
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ' '}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'links': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add links (one per line, e.g. https://yourwebsite.com)'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Add file fields separately
    profile_pic = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    cover_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add floating label support and consistent classes
        self.fields['bio'].widget.attrs.setdefault('placeholder', ' ')
        self.fields['location'].widget.attrs.setdefault('placeholder', ' ')
        self.fields['links'].widget.attrs.setdefault('placeholder', 'Add links (one per line, e.g. https://yourwebsite.com)')
        # Checkbox: ensure class for switch styling
        self.fields['is_private'].widget.attrs['class'] = 'form-check-input'

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic is None:
            return self.instance.profile_pic
        return profile_pic

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image is None:
            return self.instance.cover_image
        return cover_image

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Handle file fields safely
        if self.cleaned_data.get('profile_pic') is not None:
            instance.profile_pic = self.cleaned_data['profile_pic']
        if self.cleaned_data.get('cover_image') is not None:
            instance.cover_image = self.cleaned_data['cover_image']
        if commit:
            instance.save()
        return instance
