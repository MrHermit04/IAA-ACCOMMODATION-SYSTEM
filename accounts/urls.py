
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('rooms/', views.room_list, name='rooms'),
    path('apply/', views.apply_room_allocation, name='apply_room'),
    path('payment/<int:booking_id>/', views.payment_details, name='payment_details'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('contact/', views.contact, name='contact'),
]