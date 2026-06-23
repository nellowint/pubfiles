from django.conf import settings
from .models import WebSettings

def website_settings(request):
    settings_obj = WebSettings.objects.first()
    
    logo_url = f"{settings.STATIC_URL}img/default-logo.png"
    background_url = f"{settings.STATIC_URL}img/default-background.png"
    site_title = "Publications Website"
    
    light_primary = "#FFFFFF"
    light_secondary = "#F8F9FA"
    dark_primary = "#121212"
    dark_secondary = "#1A1A1A"

    if settings_obj:
        site_title = settings_obj.title
        light_primary = settings_obj.light_theme_primary
        light_secondary = settings_obj.light_theme_secondary
        dark_primary = settings_obj.dark_theme_primary
        dark_secondary = settings_obj.dark_theme_secondary
        
        if settings_obj.logo:
            logo_url = settings_obj.logo.url
        if settings_obj.background:
            background_url = settings_obj.background.url

    return {
        'site_title': site_title,
        'site_logo': logo_url,
        'site_favicon': logo_url,
        'site_background': background_url,
        'color_light_primary': light_primary,
        'color_light_secondary': light_secondary,
        'color_dark_primary': dark_primary,
        'color_dark_secondary': dark_secondary,
        'web_settings': settings_obj,
    }
