from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string


def robots_txt(request):
    content = render_to_string('robots.txt', {
        'seo_canonical_domain': settings.SEO_CANONICAL_DOMAIN,
    })
    return HttpResponse(content, content_type='text/plain')