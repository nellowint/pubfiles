from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('publications:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
