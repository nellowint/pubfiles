from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordResetView
from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string

from core.email import send_mail_async
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import url_has_allowed_host_and_scheme

from .models import User
from .tokens import account_verification_token
from .decorators import rate_limit


class RememberMeLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if not user.email_verified:
            form.add_error(
                None,
                'Please confirm your email before logging in. '
                'Check your inbox for the verification link.',
            )
            return self.form_invalid(form)
        remember_me = self.request.POST.get('remember_me') == 'on'
        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            self.request.session.modified = True
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class ProfileForm(forms.ModelForm):
    old_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('avatar',)
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if old_password:
            if not self.user.check_password(old_password):
                self.add_error('old_password', 'Your old password was entered incorrectly.')
            if not new_password1:
                self.add_error('new_password1', 'This field is required.')
            elif new_password1 != new_password2:
                self.add_error('new_password2', 'The two password fields didn\u2019t match.')
            else:
                validate_password(new_password1, self.user)
        elif new_password1 or new_password2:
            self.add_error('old_password', 'Enter your current password to change it.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password1')
        if new_password and self.cleaned_data.get('old_password'):
            user.set_password(new_password)
        if commit:
            user.save()
        return user


@rate_limit('register', max_attempts=3, timeout=3600)
def register_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        request.session['next_after_register'] = next_url

    if request.method == 'POST':
        if getattr(request, 'limited', False):
            form = CustomUserCreationForm()
            return render(request, 'registration/register.html', {
                'form': form,
                'rate_limited': True,
                'next_url': next_url,
            })
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email_verified = False
            user.save(update_fields=['email_verified'])

            current_site = get_current_site(request)
            subject = 'Confirm your email address'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_verification_token.make_token(user)
            confirmation_url = f'http://{current_site.domain}/confirm-email/{uid}/{token}/'

            message = render_to_string('registration/account_verification_email.html', {
                'user': user,
                'confirmation_url': confirmation_url,
                'site_title': current_site.name,
            })
            send_mail_async(subject, message, [user.email])

            return redirect('verification_sent')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {
        'form': form,
        'next_url': next_url,
    })


def verification_sent_view(request):
    return render(request, 'registration/verification_sent.html')


def confirm_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    next_url = request.session.pop('next_after_register', '')

    if user is not None and account_verification_token.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        return render(request, 'registration/email_verified.html', {
            'next_url': next_url,
        })
    else:
        return render(request, 'registration/email_verified.html', {
            'invalid_token': True,
            'next_url': next_url,
        })


class AsyncPasswordResetView(PasswordResetView):
    # Envia o e-mail de redefinição em background (mesmo comportamento do Django, só o SMTP é assíncrono)
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = render_to_string(email_template_name, context)
        send_mail_async(subject, body, [to_email], from_email=from_email)


@login_required
def profile_view(request):
    delete_form = DeleteAccountForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'remove_avatar':
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])
            return redirect('profile')

        if action == 'delete_account':
            delete_form = DeleteAccountForm(request.POST)
            if delete_form.is_valid() and request.user.check_password(delete_form.cleaned_data['password']):
                user = request.user
                auth_logout(request)
                user.delete()
                return redirect('publications:home')
            else:
                messages.error(request, 'Incorrect password. Account not deleted.')

        form = ProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user, user=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'delete_form': delete_form})


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password to confirm'}),
        label='Password',
    )
