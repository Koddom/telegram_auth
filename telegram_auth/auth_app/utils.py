import requests
from django.conf import settings


def set_telegram_webhook():
    webhook_url = f"{settings.SITE_URL}/telegram/webhook/"
    token = settings.TELEGRAM_BOT_TOKEN
    response = requests.get(f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}")
    return response.json()

