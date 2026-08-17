import random

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, Q
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView

from apps.subscriptions.models import Subscription

from .models import Category, Comment, Publication, Rating


class HomeView(ListView):
    model = Publication
    template_name = 'publications/index.html'
    context_object_name = 'publications'
    paginate_by = 20

    def get_queryset(self):
        queryset = Publication.objects.filter(is_active=True).prefetch_related('category').annotate(
            avg_rating=Avg('ratings__score'),
            ratings_count=Count('ratings'),
        )
        category_param = self.request.GET.get('category')

        if category_param:
            try:
                # Tenta buscar por slug primeiro, depois por ID (compatibilidade)
                category = Category.objects.filter(slug=category_param).first()
                if not category:
                    category = Category.objects.get(id=category_param)
                queryset = queryset.filter(
                    category__in=category.get_descendants(include_self=True)
                )
            except (Category.DoesNotExist, ValueError):
                pass

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset.order_by('-id')


class PublicationDetailView(DetailView):
    model = Publication
    template_name = 'publications/detail.html'
    context_object_name = 'publication'

    def get_queryset(self):
        return Publication.objects.filter(is_active=True).prefetch_related('category').annotate(
            avg_rating=Avg('ratings__score'),
            ratings_count=Count('ratings'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.object

        context['comments'] = (
            publication.comments.select_related('user').all()
        )

        if self.request.user.is_authenticated:
            user_rating = Rating.objects.filter(
                user=self.request.user,
                publication=publication,
            ).first()
            context['user_rating'] = user_rating.score if user_rating else 0
        else:
            context['user_rating'] = 0

        context['similar_publications'] = self.get_similar(publication)

        return context

    def get_similar(self, publication):
        base = Publication.objects.filter(is_active=True).exclude(pk=publication.pk)
        original_categories = set(publication.category.values_list('id', flat=True))
        original_words = set(w.lower() for w in publication.title.split() if len(w) > 3)

        candidates = []
        for pub in base:
            score = 0

            # Categoria (peso 10)
            pub_categories = set(pub.category.values_list('id', flat=True))
            if original_categories & pub_categories:
                score += 10

            # Título (peso 2 por palavra em comum)
            pub_words = set(w.lower() for w in pub.title.split() if len(w) > 3)
            score += len(original_words & pub_words) * 2

            # Popularidade (até 3 pontos)
            score += min(pub.views_count / 1000, 3)

            if score > 0:
                candidates.append((pub, score))

        # Ordenar por score (desc)
        candidates.sort(key=lambda x: -x[1])

        # Rotação inteligente: embaralhar dentro de grupos de 3
        groups = [candidates[i:i+3] for i in range(0, len(candidates), 3)]
        for group in groups:
            random.shuffle(group)

        # Extrair apenas as publicações (remover scores)
        result = [pub for group in groups for pub, _ in group]

        return result[:6]


@never_cache
def reader_view(request, slug, page_number):
    publication = get_object_or_404(Publication, slug=slug, is_active=True)
    all_pages = list(publication.pages.all().order_by('page_order'))
    real_total_pages = len(all_pages)

    page_number = int(page_number)

    if page_number < 1 or page_number > real_total_pages:
        return render(request, 'errors/404.html', status=404)

    if page_number == real_total_pages:
        Publication.objects.filter(pk=publication.pk).update(
            views_count=F('views_count') + 1
        )

    # Acesso total: publicações livres ou assinantes ativos.
    has_full_access = (
        not publication.is_members_only
        or (
            request.user.is_authenticated
            and Subscription.objects.is_active_for(request.user)
        )
    )

    if not has_full_access:
        accessible_pages = all_pages[:publication.free_pages_count]
        if page_number > len(accessible_pages):
            return render(
                request,
                'publications/premium.html',
                {'publication': publication},
            )
    else:
        accessible_pages = all_pages

    current_page = accessible_pages[page_number - 1]

    has_previous = page_number > 1
    has_next = page_number < real_total_pages

    context = {
        'publication': publication,
        'current_page': current_page,
        'page_number': page_number,
        'total_pages': real_total_pages,
        'real_total_pages': real_total_pages,
        'free_pages_count': publication.free_pages_count,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_page_number': page_number - 1,
        'next_page_number': page_number + 1,
        'pages': accessible_pages,
        'is_members_only': publication.is_members_only,
        'has_full_access': has_full_access,
    }

    return render(request, 'publications/reader.html', context)


@login_required
def add_comment(request, slug):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    publication = get_object_or_404(Publication, slug=slug, is_active=True)
    content = request.POST.get('content', '').strip()

    if content:
        Comment.objects.create(
            publication=publication,
            user=request.user,
            content=content,
        )

    return redirect(f"{publication.get_absolute_url()}#comentarios")


@login_required
def edit_comment(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    content = request.POST.get('content', '').strip()

    if content:
        comment.content = content
        comment.save(update_fields=['content'])

    return redirect(
        f"{comment.publication.get_absolute_url()}#comentarios"
    )


@login_required
def delete_comment(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    publication = comment.publication
    comment.delete()

    return redirect(f"{publication.get_absolute_url()}#comentarios")


@login_required
def rate_publication(request, slug):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    publication = get_object_or_404(Publication, slug=slug, is_active=True)

    try:
        score = int(request.POST.get('score', 0))
    except ValueError:
        score = 0

    if score < 1 or score > 5:
        return JsonResponse(
            {'error': 'Invalid score. Must be between 1 and 5.'},
            status=400,
        )

    Rating.objects.update_or_create(
        user=request.user,
        publication=publication,
        defaults={'score': score},
    )

    agg = publication.ratings.aggregate(
        avg=Avg('score'),
        count=Count('id'),
    )

    return JsonResponse({
        'avg_rating': round(agg['avg'], 1) if agg['avg'] else 0,
        'ratings_count': agg['count'],
        'user_rating': score,
    })
