from django.conf import settings

from apps.subscriptions.utils import has_premium_access

from .models import WebSettings

def website_settings(request):
    settings_obj = WebSettings.objects.first()
    
    logo_url = f"{settings.STATIC_URL}img/default-logo.png"
    background_url = f"{settings.STATIC_URL}img/default-background.png"
    background_mobile_url = None
    site_title = "Publications Website"
    site_subtitle = ""
    site_description = ""
    
    light_primary = "#FFFFFF"
    light_secondary = "#F8F9FA"
    dark_primary = "#121212"
    dark_secondary = "#1A1A1A"

    if settings_obj:
        site_title = settings_obj.title
        site_subtitle = settings_obj.subtitle
        site_description = settings_obj.description
        light_primary = settings_obj.light_theme_primary
        light_secondary = settings_obj.light_theme_secondary
        dark_primary = settings_obj.dark_theme_primary
        dark_secondary = settings_obj.dark_theme_secondary
        
        if settings_obj.logo:
            logo_url = settings_obj.logo.url
        if settings_obj.background:
            background_url = settings_obj.background.url
        if settings_obj.background_mobile:
            background_mobile_url = settings_obj.background_mobile.url

    website_banners = []
    if settings_obj:
        qs = settings_obj.banners.filter(is_active=True)
        # premium não vê banners com anúncio, mantém só banners de imagem pura
        if has_premium_access(request.user):
            qs = qs.filter(advertisement__isnull=True)
        website_banners = list(qs)

    seo_keywords = []
    if settings_obj and getattr(settings_obj, 'seo_keywords', ''):
        seo_keywords = [k.strip() for k in settings_obj.seo_keywords.split(',') if k.strip()]

    # variante sem espaços para SEO (ex: "Site HQ" -> "SiteHQ") — ajuda Google a associar "site hq" e "sitehq"
    site_title_compact = site_title.replace(" ", "") if site_title else ""

    # SocialMedia — múltiplas redes (X, Instagram, Facebook, TikTok, YouTube)
    social_media = []
    site_social_sameAs = []
    site_twitter_url = ""
    site_twitter_handle = ""
    if settings_obj:
        try:
            qs_social = settings_obj.social_media.filter(is_active=True).order_by('order')
            social_media = list(qs_social)
            site_social_sameAs = [s.url for s in social_media if s.url]
            # primeiro X para twitter:site
            for s in social_media:
                if s.platform == 'x' and s.url:
                    site_twitter_url = s.url.strip()
                    handle = site_twitter_url.rstrip("/").split("/")[-1]
                    if handle:
                        if not handle.startswith("@"):
                            handle = "@" + handle
                        site_twitter_handle = handle
                    break
        except Exception:
            pass
        # fallback legado: twitter_url single field (antes da migração para SocialMedia)
        if not site_twitter_url and getattr(settings_obj, 'twitter_url', ''):
            site_twitter_url = settings_obj.twitter_url.strip()
            if site_twitter_url:
                handle = site_twitter_url.rstrip("/").split("/")[-1]
                if handle:
                    if not handle.startswith("@"):
                        handle = "@" + handle
                    site_twitter_handle = handle
                if site_twitter_url not in site_social_sameAs:
                    site_social_sameAs = [site_twitter_url] + site_social_sameAs

    return {
        'site_title': site_title,
        'site_title_compact': site_title_compact,
        'social_media': social_media,
        'site_social_sameAs': site_social_sameAs,
        'site_twitter_url': site_twitter_url,
        'site_twitter_handle': site_twitter_handle,
        'site_subtitle': site_subtitle,
        'site_description': site_description,
        'site_logo': logo_url,
        'site_favicon': logo_url,
        'site_background': background_url,
        'site_background_mobile': background_mobile_url or background_url,
        'color_light_primary': light_primary,
        'color_light_secondary': light_secondary,
        'color_dark_primary': dark_primary,
        'color_dark_secondary': dark_secondary,
        'web_settings': settings_obj,
        'seo_keywords': seo_keywords,
        'seo_canonical_domain': settings.SEO_CANONICAL_DOMAIN,
        'website_banners': website_banners,
    }
