# billing/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('provider/home/', views.provider_home, name='provider_home'),
    path('send-bill/<int:user_id>/', views.send_bill, name='send_bill'),
    path('bill-history/', views.bill_history, name='bill_history'),
    path('sent-bill-history/', views.sent_bill_history, name='sent_bill_history'),
    path('bill/<int:bill_id>/', views.bill_detail, name='bill_detail'),  # Add this line
]