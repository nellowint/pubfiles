from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView

from apps.subscriptions.models import Subscription

from .models import Category, Publication


class HomeView(ListView):
    model = Publication
    template_name = 'publications/index.html'
    context_object_name = 'publications'
    paginate_by = 12

    def get_queryset(self):
        queryset = Publication.objects.all()
        category_id = self.request.GET.get('category')

        if category_id:
            try:
                category = Category.objects.get(id=category_id)

                queryset = queryset.filter(category__in=category.get_descendants(include_self=True))
            except (Category.DoesNotExist, ValueError):
                pass

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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
        has_access = (
            request.user.is_authenticated
            and Subscription.objects.is_active_for(request.user)
        )
        if not has_access:
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
