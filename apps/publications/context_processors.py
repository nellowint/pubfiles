from apps.categories.models import Category


def categories_processor(request):
    """Context processor para disponibilizar categorias em todas as páginas."""
    return {
        'categories': Category.objects.all(),
    }
