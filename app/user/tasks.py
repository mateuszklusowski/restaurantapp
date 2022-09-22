from celery import shared_task

from django.core.mail import send_mail
from django.conf import settings

from oauth2_provider.models import clear_expired


@shared_task
def send_reset_password_email(email_subject, email_body, to_whom):
    return send_mail(
        subject=email_subject,
        message=email_body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_whom]
    )


@shared_task
def clear_expired_tokens():
    return clear_expired()
