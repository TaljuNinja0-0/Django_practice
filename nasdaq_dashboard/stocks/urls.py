from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('add/', views.stock_add, name='stock_add'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
]