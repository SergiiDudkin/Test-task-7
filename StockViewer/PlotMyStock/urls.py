from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('tickers/<str:symbol>/<str:period>/<str:interval>/', views.show_ticker, name='show_ticker'),
]
