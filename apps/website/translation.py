from modeltranslation.translator import TranslationOptions, register

from .models import WebSettings


@register(WebSettings)
class WebSettingsTranslationOptions(TranslationOptions):
    fields = ('subtitle', 'description', 'privacy_policy', 'terms', 'start_message')
    empty_values = ''
