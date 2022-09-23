from celery import shared_task
import httpx
import os


@shared_task
def get_average_delivery_time(origins_address, order_address):
    url = "https://api.distancematrix.ai/maps/api/distancematrix/json?"

    params = {
        'origins': origins_address,
        'destinations': order_address,
        'key': os.environ.get('MATRIX_KEY')
    }

    try:
        response = httpx.post(url, params=params, json=True)
        is_zero = response.json()['rows'][0]['elements'][0]['status']

        if is_zero == 'ZERO_RESULTS':
            return 'Average delivery time cannot be calculated'

        return response.json()['rows'][0]['elements'][0]['duration']['text']
    except RuntimeError:
        return 'Average delivery time cannot be calculated'
