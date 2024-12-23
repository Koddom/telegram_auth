from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('telegram/callback/', views.telegram_callback, name='telegram_callback'),
]
