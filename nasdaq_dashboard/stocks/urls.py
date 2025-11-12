from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('add/', views.stock_add, name='stock_add'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),  # 상세 페이지 추가
]