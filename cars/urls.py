from django.urls import path
from . import views

urlpatterns = [
    path('', views.car_list, name='car_list'),
    path('car/<int:pk>/', views.car_detail, name='car_detail'),
    path('post/', views.post_car, name='post_car'),
    path('notifications/', views.notifications, name='notifications'),
    path('approve/<int:car_id>/', views.approve_car, name='approve_car'),
    path('buy/<int:car_id>/', views.buy_car, name='buy_car'),
    path('sold/<int:car_id>/', views.mark_sold, name='mark_sold'),
]
