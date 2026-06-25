from modeltranslation.translator import TranslationOptions, register

from .models import Publication


@register(Publication)
class PublicationTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    empty_values = ''
