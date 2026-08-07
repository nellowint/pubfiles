from modeltranslation.translator import TranslationOptions, register

from .models import WebSettings


@register(WebSettings)
class WebSettingsTranslationOptions(TranslationOptions):
    fields = ('privacy_policy', 'terms')
    empty_values = ''
