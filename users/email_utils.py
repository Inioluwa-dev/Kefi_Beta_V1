from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


def send_welcome_email(user, request=None):
    """
    Send a welcome email to a newly registered user
    """
    try:
        # Get site URL
        if request:
            site_url = f"{request.scheme}://{request.get_host()}"
        else:
            site_url = getattr(settings, 'SITE_URL', 'https://kefi.onrender.com')
        
        # Ensure we don't use localhost in production
        if 'localhost' in site_url or '127.0.0.1' in site_url:
            site_url = 'https://kefi.onrender.com'
        
        # Render email template
        html_content = render_to_string('emails/welcome_email.html', {
            'user': user,
            'site_url': site_url,
        })
        
        # Create email
        subject = f"🎉 Welcome to Kefi, {user.first_name or user.username}!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Welcome to Kefi! Your account has been created successfully. Visit {site_url} to start connecting with other students.",
            from_email=from_email,
            to=to_email,
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_verification_email(email, code, request=None):
    """
    Send email verification code with improved design
    """
    try:
        # Render email template
        html_content = render_to_string('emails/verification_email.html', {
            'code': code,
            'email': email,
        })
        
        # Create email
        subject = "🔐 Verify Your Email - Kefi"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Your Kefi verification code is: {code}. Enter this code to complete your registration.",
            from_email=from_email,
            to=to_email,
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_password_reset_email(user, request, token, uid):
    """
    Send password reset email with improved design
    """
    try:
        # Get site info
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'
        
        # Render email template
        html_content = render_to_string('emails/password_reset_email.html', {
            'user': user,
            'domain': domain,
            'protocol': protocol,
            'uid': uid,
            'token': token,
        })
        
        # Create email
        subject = "🔑 Reset Your Password - Kefi"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Click the link to reset your password: {protocol}://{domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}",
            from_email=from_email,
            to=to_email,
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
