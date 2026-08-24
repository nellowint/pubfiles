from django import template

register = template.Library()


@register.filter
def get_item(lst, index):
    """Retorna o item do índice especificado, ou None se não existir."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return None