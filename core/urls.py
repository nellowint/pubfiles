from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path

from apps.accounts.views import (
    register_view, RememberMeLoginView, profile_view,
    verification_sent_view, confirm_email_view,
)
from apps.publications.sitemaps import PublicationSitemap, StaticSitemap
from apps.website.views import robots_txt

sitemaps = {
    'publications': PublicationSitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path('health/', lambda request: HttpResponse('OK', content_type='text/plain')),

    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path('admin/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),

    path('login/', RememberMeLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),
    path('verification-sent/', verification_sent_view, name='verification_sent'),
    path('confirm-email/<uidb64>/<token>/', confirm_email_view, name='confirm_email'),
    path('profile/', profile_view, name='profile'),

    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('', include('apps.publications.urls')),
    path('', include('apps.website.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

handler404 = lambda request, exception: render(request, 'errors/404.html', status=404)
