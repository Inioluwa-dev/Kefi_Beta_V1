from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import Profile
from django.http import HttpResponseRedirect
from django.urls import reverse

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:home')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')

@login_required
def profile_view(request, username):
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
    profile = request.user.profile
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
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    user_profile = request.user.profile
    if target_profile != user_profile:
        user_profile.following.add(target_profile)  # Add Profile, not User!
        messages.success(request, f'You are now following {target_user.username}.')
    return redirect('users:profile', username=username)

@login_required
def unfollow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    user_profile = request.user.profile
    if target_profile != user_profile:
        user_profile.following.remove(target_profile)  # Remove Profile, not User!
        messages.info(request, f'You have unfollowed {target_user.username}.')
    return redirect('users:profile', username=username)
