from django import template

register = template.Library()


@register.filter
def username_only(value):
    return value.split('@')[0] if value else ''


@register.inclusion_tag('publications/_category_nav_children.html', takes_context=True)
def render_nav_children(context, category):
    return {'category': category}


@register.inclusion_tag('publications/_category_drawer_children.html', takes_context=True)
def render_drawer_children(context, category):
    return {'category': category}