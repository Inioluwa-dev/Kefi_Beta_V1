from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import Profile
from django.http import HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.urls import reverse
from kefi_beta_version1.views import custom_404_view
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import PasswordResetConfirmView
import random
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

class ReactivatePasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        user = form.save()
        user.is_active = True
        user.save()
        return super().form_valid(form)

def is_email_verified(email):
    from django.contrib.auth.models import User
    user = User.objects.filter(email=email).first()
    return bool(user and hasattr(user, 'profile') and user.profile.email_verified)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        email = request.POST.get('email')
        if form.is_valid():
            if not is_email_verified(email):
                form.add_error('email', 'Please verify your email before signing up.')
            else:
                user = form.save()
                # Clear verification session keys
                request.session.pop('email_verified', None)
                request.session.pop('email_verification_code', None)
                request.session.pop('email_verification_target', None)
                messages.success(request, 'Account created! You can now log in.')
                return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    show_login_required = request.GET.get('login_required') == '1'
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('posts:feed')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form, 'show_login_required': show_login_required, 'next': next_url})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')

def profile_view(request, username):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/profile/{username}/&login_required=1")
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile
    # Only show unblocked posts to everyone, including the owner
    posts = user_obj.posts.filter(blocked=False).order_by('-created_at')
    return render(request, 'users/profile.html', {
        'user_obj': user_obj,
        'profile': profile,
        'posts': posts,
    })

@login_required
def edit_profile_view(request):
    if not request.user.is_authenticated:
        return custom_404_view(request)
    profile = request.user.profile
    
    # Ensure profile exists and has safe file fields
    try:
        # Check if profile has problematic file fields
        if hasattr(profile, 'cover_image') and profile.cover_image:
            # Test if the file actually exists
            try:
                profile.cover_image.url
            except (ValueError, OSError):
                # File doesn't exist, set to None
                profile.cover_image = None
                profile.save()
        
        if hasattr(profile, 'profile_pic') and profile.profile_pic:
            try:
                profile.profile_pic.url
            except (ValueError, OSError):
                # File doesn't exist, set to default
                profile.profile_pic = 'profile_pics/default.jpg'
                profile.save()
                
    except Exception as e:
        # If there's any issue with the profile, create a fresh one
        Profile.objects.filter(user=request.user).delete()
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def follow_view(request, username):
    if not request.user.is_authenticated:
        return custom_404_view(request)
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    user_profile = request.user.profile
    if target_profile != user_profile:
        user_profile.following.add(target_profile)  # Add Profile, not User!
        messages.success(request, f'You are now following {target_user.username}.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('users:profile', username=username)

@login_required
def unfollow_view(request, username):
    if not request.user.is_authenticated:
        return custom_404_view(request)
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    user_profile = request.user.profile
    if target_profile != user_profile:
        user_profile.following.remove(target_profile)  # Remove Profile, not User!
        messages.info(request, f'You have unfollowed {target_user.username}.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('users:profile', username=username)

@login_required
def deactivate_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        auth_logout(request)
        messages.info(request, 'Your account has been deactivated.')
        return redirect('users:login')
    return render(request, 'users/deactivate_account.html')

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        auth_logout(request)
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('users:register')
    return render(request, 'users/delete_account.html')

@login_required
def settings_view(request):
    profile = request.user.profile
    # Ensure profile exists and has safe file fields
    try:
        if hasattr(profile, 'cover_image') and profile.cover_image:
            try:
                profile.cover_image.url
            except (ValueError, OSError):
                profile.cover_image = None
                profile.save()
        if hasattr(profile, 'profile_pic') and profile.profile_pic:
            try:
                profile.profile_pic.url
            except (ValueError, OSError):
                profile.profile_pic = 'profile_pics/default.jpg'
                profile.save()
    except Exception:
        Profile.objects.filter(user=request.user).delete()
        profile = Profile.objects.create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:settings')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'users/settings.html', {'form': form, 'profile': profile})

def privacy_policy_view(request):
    return render(request, 'users/privacy_policy.html')

def terms_of_service_view(request):
    return render(request, 'users/terms_of_service.html')

def cookie_policy_view(request):
    return render(request, 'users/cookie_policy.html')

@require_POST
@csrf_exempt
def send_verification_code(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'success': False, 'error': 'No email provided.'}, status=400)
    code = str(random.randint(100000, 999999))
    request.session['email_verification_code'] = code
    request.session['email_verification_target'] = email
    send_mail(
        'Your Kefi Email Verification Code',
        f'Your verification code is: {code}',
        None,
        [email],
        fail_silently=False,
    )
    return JsonResponse({'success': True})

@require_POST
@csrf_exempt
def verify_code(request):
    code = request.POST.get('code')
    email = request.POST.get('email')
    session_code = request.session.get('email_verification_code')
    session_email = request.session.get('email_verification_target')
    if code and email and code == session_code and email == session_email:
        request.session['email_verified'] = True
        # Persistently mark the user's profile as verified if the user exists
        from django.contrib.auth.models import User
        user = User.objects.filter(email=email).first()
        if user and hasattr(user, 'profile'):
            user.profile.email_verified = True
            user.profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid code or email.'}, status=400)

def user_exists_view(request):
    username = request.GET.get('username', '').strip()
    from django.contrib.auth.models import User
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def email_verified_view(request):
    email = request.GET.get('email', '').strip()
    from django.contrib.auth.models import User
    user = User.objects.filter(email=email).first()
    verified = False
    if user and hasattr(user, 'profile'):
        verified = user.profile.email_verified
    return JsonResponse({'verified': verified})
