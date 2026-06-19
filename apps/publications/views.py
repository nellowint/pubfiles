from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.http import HttpResponseForbidden
from apps.website.models import CarouselBanner
from django.db.models import Q
from .models import Publication, Category

class HomeView(ListView):
    model = Publication
    template_name = 'publications/index.html'
    context_object_name = 'publications'
    paginate_by = 12

    def get_queryset(self):
        # Pega o banco de dados inicial de publicações ativas
        queryset = Publication.objects.all() # ou .filter(active=True) se você tiver esse campo

        # 1. Captura o ID da categoria vindo da URL (?category=1)
        category_id = self.request.GET.get('category')

        if category_id:
            try:
                # Buscamos a categoria selecionada pelo ID
                category = Category.objects.get(id=category_id)

                # VANTAGEM DO MPTT: Filtrar a categoria pai traz ela E TODAS as filhas automaticamente!
                queryset = queryset.filter(category__in=category.get_descendants(include_self=True))
            except (Category.DoesNotExist, ValueError):
                # Se mandarem um ID inválido na URL, não filtra nada (evita quebrar a página)
                pass

        # 2. Captura a busca por texto se houver (?q=termo)
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset.order_by('-id') # Ajuste a ordenação como preferir

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Garante que a lista de categorias e banners continuem indo para o HTML herdeiro do base.html
        context['categories'] = Category.objects.all()
        # context['banners'] = Banner.objects.all() # Ative se tiver o model de banners
        return context

class PublicationDetailView(DetailView):
    model = Publication
    template_name = 'publications/detail.html'
    context_object_name = 'publication'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

@never_cache
def reader_view(request, slug, page_number):
    publication = get_object_or_404(Publication, slug=slug)
    all_pages = publication.pages.all().order_by('page_order')
    total_pages = all_pages.count()

    page_number = int(page_number)

    if page_number < 1 or page_number > total_pages:
        return render(request, 'errors/404.html', status=404)

    current_page = all_pages[page_number - 1]

    if publication.is_members_only and page_number > publication.free_pages_count:
        if not request.user.is_authenticated:
            return render(request, 'publications/premium.html', {'publication': publication})

    has_previous = page_number > 1
    has_next = page_number < total_pages

    context = {
        'publication': publication,
        'current_page': current_page,
        'page_number': page_number,
        'total_pages': total_pages,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_page_number': page_number - 1,
        'next_page_number': page_number + 1,
    }

    return render(request, 'publications/reader.html', context)
