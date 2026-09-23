import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def is_recaptcha_configured():
    return bool(settings.RECAPTCHA_SITE_KEY and settings.RECAPTCHA_SECRET_KEY)


def verify_recaptcha_token(token):
    """Valida o token do reCAPTCHA v2 na API siteverify do Google.

    Retorna True apenas quando a resposta é bem-sucedida. Fail-closed:
    qualquer erro de rede ou parsing retorna False. Quando não há chaves
    configuradas (dev/teste local), a verificação é pulada e True é retornado.
    """
    if not is_recaptcha_configured():
        return True
    if not token:
        return False
    try:
        response = requests.post(
            VERIFY_URL,
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": token,
            },
            timeout=settings.RECAPTCHA_TIMEOUT,
        )
        result = response.json()
    except Exception:
        logger.warning("recaptcha verification request failed")
        return False
    return bool(result.get("success"))
