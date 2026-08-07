from django.urls import path
from django.views.generic import TemplateView

from apps.website.models import WebSettings


class PrivacyView(TemplateView):
    template_name = 'website/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj = WebSettings.objects.first()
        context['content'] = settings_obj.privacy_policy if settings_obj else ''
        return context


class TermsView(TemplateView):
    template_name = 'website/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj = WebSettings.objects.first()
        context['content'] = settings_obj.terms if settings_obj else ''
        return context


urlpatterns = [
    path('privacy/', PrivacyView.as_view(), name='privacy_policy'),
    path('terms/', TermsView.as_view(), name='terms'),
]
