# dashboard/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from accounts.models import Provider, UserProfile
from billing.models import Bill
from payments.models import Payment
from .models import ProviderSubscription

@login_required
def user_dashboard(request):
    if request.user.userprofile.is_provider:
        return redirect('provider_dashboard')
    
    recent_bills = Bill.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_paid = Payment.objects.filter(
        bill__user=request.user,
        status='Success'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    upcoming_bills = Bill.objects.filter(
        user=request.user,
        status='Unpaid',
        due_date__gte=timezone.now()
    ).order_by('due_date')[:3]
    
    monthly_spending = Payment.objects.filter(
        bill__user=request.user,
        status='Success',
        payment_date__month=timezone.now().month
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    context = {
        'recent_bills': recent_bills,
        'total_paid': total_paid,
        'upcoming_bills': upcoming_bills,
        'monthly_spending': monthly_spending
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)

@login_required
def provider_dashboard(request):
    if not request.user.userprofile.is_provider:
        return redirect('user_dashboard')
    
    provider = request.user.userprofile.provider
    recent_bills = Bill.objects.filter(
        provider=provider
    ).order_by('-created_at')[:5]
    
    total_received = Payment.objects.filter(
        bill__provider=provider,
        status='Success'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    context = {
        'recent_bills': recent_bills,
        'total_received': total_received
    }
    
    return render(request, 'dashboard/provider_dashboard.html', context)

@login_required
def provider_services(request):
    all_providers = Provider.objects.all()
    subscribed_providers = ProviderSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).values_list('provider_id', flat=True)
    
    context = {
        'providers': all_providers,
        'subscribed_providers': subscribed_providers
    }
    
    return render(request, 'dashboard/provider_services.html', context)

@login_required
def subscribe_provider(request, provider_id):
    provider = Provider.objects.get(id=provider_id)
    
    subscription, created = ProviderSubscription.objects.get_or_create(
        user=request.user,
        provider=provider,
        defaults={'is_active': True}
    )
    
    if not created:
        subscription.is_active = True
        subscription.save()
    
    messages.success(request, f'Successfully subscribed to {provider.provider_name}')
    return redirect('provider_services')

@login_required
def unsubscribe_provider(request, provider_id):
    subscription = ProviderSubscription.objects.get(
        user=request.user,
        provider_id=provider_id
    )
    subscription.is_active = False
    subscription.save()
    
    messages.success(request, 'Successfully unsubscribed from provider')
    return redirect('provider_services')

@login_required
def provider_users(request):
    if not request.user.userprofile.is_provider:
        return redirect('user_dashboard')
    
    provider = request.user.userprofile.provider
    subscriptions = ProviderSubscription.objects.filter(
        provider=provider,
        is_active=True
    ).select_related('user')
    
    return render(request, 'dashboard/provider_users.html', {'subscriptions': subscriptions})

@login_required
def generate_payment_report(request):
    if request.user.userprofile.is_provider:
        provider = request.user.userprofile.provider
        payments = Payment.objects.filter(
            bill__provider=provider,
            status='Success'
        ).select_related('bill', 'bill__user')
    else:
        payments = Payment.objects.filter(
            bill__user=request.user,
            status='Success'
        ).select_related('bill', 'bill__provider')
    
    monthly_stats = {}
    for payment in payments:
        month_key = payment.payment_date.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                'total': 0,
                'count': 0
            }
        monthly_stats[month_key]['total'] += payment.amount_paid
        monthly_stats[month_key]['count'] += 1
    
    context = {
        'monthly_stats': sorted(monthly_stats.items()),
        'total_amount': sum(p.amount_paid for p in payments),
        'total_count': len(payments)
    }
    
    return render(request, 'dashboard/payment_report.html', context)

@login_required
def bill_analytics(request):
    if request.user.userprofile.is_provider:
        provider = request.user.userprofile.provider
        bills = Bill.objects.filter(provider=provider)
    else:
        bills = Bill.objects.filter(user=request.user)
    
    bill_type_stats = bills.values('bill_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    status_stats = bills.values('status').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    context = {
        'bill_type_stats': bill_type_stats,
        'status_stats': status_stats
    }
    
    return render(request, 'dashboard/bill_analytics.html', context)