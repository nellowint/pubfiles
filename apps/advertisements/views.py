import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
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


@require_GET
def ad_redirect(request, ad_id):
    try:
        ad = Advertisements.objects.get(id=ad_id, is_active=True)
        ad.ratings_count += 1
        ad.save(update_fields=['ratings_count'])
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Advertisement</title>
    <style>
        body {{ margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; }}
    </style>
</head>
<body>
    {ad.link}
</body>
</html>'''
        return HttpResponse(html)
    except Advertisements.DoesNotExist:
        return HttpResponse('Ad not found', status=404)
