from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('tickers/<str:symbol>/', views.show_ticker, name='show_ticker'),
]
