import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.conf import settings
from .models import CustomUser
from secrets import token_urlsafe
import requests


# Хранилище токенов авторизации
auth_tokens = {}


def index(request):
    if request.user.is_authenticated:
        return render(request, 'auth_app/index.html', {'username': request.user.username})
    else:
        token = token_urlsafe(16)
        request.session['auth_token'] = token
        auth_tokens[token] = None
        telegram_url = f"https://t.me/{settings.TELEGRAM_BOT_NAME}?start={token}"
        return render(request, 'auth_app/index.html', {'telegram_url': telegram_url})


@csrf_exempt
def telegram_webhook(request):
    print('telegram_webhook')
    if request.method == "POST":
        try:
            # Получаем данные, отправленные через webhook
            data = json.loads(request.body)

            # Проверяем, что в сообщении есть текст и что это команда /start
            if "message" in data and "text" in data["message"]:
                text = data["message"]["text"]
                if text.startswith("/start"):
                    # Извлекаем токен из команды /start
                    token = text.split(" ")[-1]
                    telegram_id = data["message"]["from"]["id"]
                    telegram_username = data["message"]["from"].get("username", None)

                    # Сохраняем информацию о токене в auth_tokens
                    auth_tokens[token] = {
                        "telegram_id": telegram_id,
                        "telegram_username": telegram_username
                    }
                    print(auth_tokens)

                    # Ответ пользователю в Telegram
                    chat_id = data["message"]["chat"]["id"]
                    url = f'https://{settings.SITE_URL}/telegram/callback/?token={token}'
                    response_text = f"Для авторизации через Telegram перейдите по ссылке {url}."
                    send_telegram_message(chat_id, response_text)

            return JsonResponse({"status": "ok"})
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({"error": "Invalid request"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def send_telegram_message(chat_id, text):
    """Отправка сообщения пользователю через Telegram API."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Проверяем на ошибки
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")


def telegram_callback(request):
    print('telegram_callback')
    token = request.GET.get('token')
    user_data = auth_tokens.get(token)
    print(auth_tokens)
    print('user_data: ', user_data)
    if user_data:
        user = CustomUser.objects.filter(telegram_id=user_data["telegram_id"]).first()

        if not user:
            user = CustomUser.objects.create_user(
                username=f"tg_user_{user_data['telegram_id']}" or user_data["telegram_username"],
                telegram_id=user_data["telegram_id"],
                telegram_username=user_data["telegram_username"],
                # password=CustomUser.objects.make_random_password()
            )
        print(login(request, user))

        return redirect('index')

    return JsonResponse({"error": "Invalid token"}, status=400)
