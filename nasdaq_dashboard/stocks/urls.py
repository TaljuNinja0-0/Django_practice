from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('add/', views.stock_add, name='stock_add'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
]