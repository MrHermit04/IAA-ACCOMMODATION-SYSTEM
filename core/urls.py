from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]