import logging
import threading
import time

from django.core.mail import send_mail

logger = logging.getLogger(__name__)

RETRY_ATTEMPTS = 3


def _send_with_retry(subject, message, from_email, recipient_list, html_message=None):
    # Só o SMTP roda em background; renderização fica na view (precisa de request)
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            send_mail(subject, message, from_email, recipient_list, html_message=html_message)
            return
        except Exception:
            if attempt == RETRY_ATTEMPTS:
                logger.exception('Falha ao enviar e-mail para %s', recipient_list)
            else:
                time.sleep(2 * attempt)


def send_mail_async(subject, message, recipient_list, from_email=None, html_message=None):
    thread = threading.Thread(
        target=_send_with_retry,
        args=(subject, message, from_email, recipient_list, html_message),
        daemon=True,
    )
    thread.start()
    return thread
