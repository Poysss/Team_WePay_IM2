from django.urls import path
from . import views

urlpatterns = [
    path('options/', views.payment_options, name='payment_options'),
    path('cash-in/<int:method_id>/', views.cash_in, name='cash_in'),
    path('make-payment/<int:bill_id>/', views.make_payment, name='make_payment'),
    path('payment-success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('remove-method/<int:method_id>/', views.remove_payment_method, name='remove_payment_method'),
]