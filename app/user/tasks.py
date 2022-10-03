from celery import shared_task

import httpx

import os

from app.wsgi import application

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


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
    from oauth2_provider.models import clear_expired
    clear_expired()


@shared_task
def generate_token(domain, **params):
    data = {
        'grant_type': os.environ.get('GRANT_TYPE1'),
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': os.environ.get('CLIENT_SECRET')
    }
    data.update(**params)

    with httpx.Client(app=application, base_url=f'https://{domain}') as client:
        response = client.post(reverse('drf:token'), json=data)
    return response.json()
