from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.static import serve

from apps.accounts.views import (
    register_view, RememberMeLoginView, profile_view,
    verification_sent_view, confirm_email_view,
)
from apps.publications.sitemaps import PublicationSitemap, StaticSitemap
from apps.website.views import robots_txt


def no_cache_serve(request, path, document_root=None, **kwargs):
    """Serve arquivos estáticos/mídia com headers anti-cache em desenvolvimento."""
    response = serve(request, path, document_root=document_root, **kwargs)
    if settings.DEBUG:
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Last-Modified'] = None
    return response

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
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', no_cache_serve, {'document_root': settings.STATICFILES_DIRS[0]}),
        re_path(r'^media/(?P<path>.*)$', no_cache_serve, {'document_root': settings.MEDIA_ROOT}),
    ]

handler404 = lambda request, exception: render(request, 'errors/404.html', status=404)
