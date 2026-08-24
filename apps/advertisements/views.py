from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Advertisements


@csrf_exempt
@require_POST
def increment_click(request, ad_id):
    try:
        ad = Advertisements.objects.get(id=ad_id, is_active=True)
        ad.ratings_count += 1
        ad.save(update_fields=['ratings_count'])
        return JsonResponse({
            'success': True,
            'clicks': ad.ratings_count,
            'is_url': not ad.is_script,
            'link': ad.link if not ad.is_script else None
        })
    except Advertisements.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ad not found'}, status=404)
