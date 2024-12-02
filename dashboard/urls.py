# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # User Dashboard URLs
    path('', views.user_dashboard, name='user_dashboard'),
    path('providers/', views.provider_services, name='provider_services'),
    path('providers/subscribe/<int:provider_id>/', views.subscribe_provider, name='subscribe_provider'),
    path('providers/unsubscribe/<int:provider_id>/', views.unsubscribe_provider, name='unsubscribe_provider'),
    
    # Provider Dashboard URLs
    path('provider/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/users/', views.provider_users, name='provider_users'),
    
    # Reports and Analytics URLs
    path('reports/payments/', views.generate_payment_report, name='payment_report'),
    path('analytics/bills/', views.bill_analytics, name='bill_analytics'),
]