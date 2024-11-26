# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import (
    SimpleUserCreationForm, 
    SimpleProviderCreationForm, 
    UserProfileUpdateForm, 
    ProviderProfileUpdateForm, 
    PasswordChangeCustomForm
)
from .models import UserProfile, Provider
from django.core.exceptions import PermissionDenied

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        if self.request.user.userprofile.is_provider:
            return reverse_lazy('provider_home')
        return reverse_lazy('user_home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

def register_user(request):
    if request.user.is_authenticated:
        return redirect('user_home')
        
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('user_home')
    else:
        form = SimpleUserCreationForm()
    return render(request, 'accounts/register_user.html', {'form': form})

def register_provider(request):
    if request.user.is_authenticated:
        return redirect('provider_home')
        
    if request.method == 'POST':
        form = SimpleProviderCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Provider registration successful!')
            return redirect('provider_home')
    else:
        form = SimpleProviderCreationForm()
    return render(request, 'accounts/register_provider.html', {'form': form})

@login_required
def profile_view(request):
    if request.user.userprofile.is_provider:
        return redirect('provider_profile')
    
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=user_profile)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def provider_profile(request):
    if not request.user.userprofile.is_provider:
        return redirect('profile')
    
    provider = request.user.userprofile.provider
    if request.method == 'POST':
        form = ProviderProfileUpdateForm(request.POST, instance=provider)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, 'Provider profile updated successfully!')
            return redirect('provider_profile')
    else:
        form = ProviderProfileUpdateForm(instance=provider)
    
    return render(request, 'accounts/provider_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['current_password']):
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('profile' if not user.userprofile.is_provider else 'provider_profile')
            else:
                messages.error(request, 'Current password is incorrect!')
    else:
        form = PasswordChangeCustomForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def user_home(request):
    if request.user.userprofile.is_provider:
        return redirect('provider_home')
    return render(request, 'accounts/user_home.html')

@login_required
def provider_home(request):
    if not request.user.userprofile.is_provider:
        return redirect('user_home')
    return render(request, 'accounts/provider_home.html')