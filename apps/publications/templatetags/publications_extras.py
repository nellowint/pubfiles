from django import template

register = template.Library()


@register.filter
def username_only(value):
    return value.split('@')[0] if value else ''
