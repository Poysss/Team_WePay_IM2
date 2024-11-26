from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Sum  # Added Sum
from accounts.models import Provider, UserProfile
from dashboard.models import ProviderSubscription  # Add this import
from payments.models import Payment  # Add this import
from .models import Bill
from .forms import BillForm
from notifications.views import create_notification


@login_required
def provider_home(request):
    if not request.user.userprofile.is_provider:
        messages.error(request, "Access denied. Provider account required.")
        return redirect('login')
    
    provider = request.user.userprofile.provider
    
    # Get all subscribers
    subscribers = ProviderSubscription.objects.filter(
        provider=provider,
        is_active=True
    ).select_related('user', 'user__userprofile')
    
    # Get recent bills
    recent_bills = Bill.objects.filter(
        provider=provider
    ).order_by('-created_at')[:5]
    
    # Get payment statistics
    total_received = Payment.objects.filter(
        bill__provider=provider,
        status='Success'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Get unpaid bills count
    unpaid_bills = Bill.objects.filter(
        provider=provider,
        status='Unpaid'
    ).count()
    
    context = {
        'subscribers': subscribers,
        'recent_bills': recent_bills,
        'total_received': total_received,
        'unpaid_bills': unpaid_bills,
        'subscriber_count': subscribers.count()
    }
    
    return render(request, 'billing/provider_home.html', context)

login_required
def send_bill(request, user_id):
    if not request.user.userprofile.is_provider:
        messages.error(request, "Access denied. Provider account required.")
        return redirect('login')
    
    provider = request.user.userprofile.provider
    user = get_object_or_404(User, id=user_id)
    
    # Check if user is a subscriber
    subscription = get_object_or_404(ProviderSubscription, 
        provider=provider, 
        user=user,
        is_active=True
    )
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.provider = provider
            bill.user = user
            bill.save()
            
            # Create notification for the user
            create_notification(
                user=user,
                notification_type='bill_received',
                title=f'New Bill from {provider.provider_name}',
                message=f'You have received a new {bill.bill_type} bill for ${bill.amount}',
                related_bill=bill
            )
            
            messages.success(request, f"Bill sent to {user.username} successfully!")
            return redirect('provider_home')
    else:
        form = BillForm()
    
    return render(request, 'billing/send_bill.html', {
        'form': form,
        'user': user
    })

@login_required
def bill_history(request):
    if request.user.userprofile.is_provider:
        bills = Bill.objects.filter(provider=request.user.userprofile.provider)
    else:
        bills = Bill.objects.filter(user=request.user)
    
    return render(request, 'billing/bill_history.html', {
        'bills': bills
    })

@login_required
def sent_bill_history(request):
    if not request.user.userprofile.is_provider:
        messages.error(request, "Access denied. Provider account required.")
        return redirect('login')
    
    provider = request.user.userprofile.provider
    bills = Bill.objects.filter(provider=provider).order_by('-created_at')
    
    return render(request, 'billing/sent_bill_history.html', {
        'bills': bills
    })


@login_required
def send_bill(request, user_id):
    if not request.user.userprofile.is_provider:
        messages.error(request, "Access denied. Provider account required.")
        return redirect('login')
    
    provider = request.user.userprofile.provider
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.provider = provider
            bill.user = user
            bill.save()
            
            # Create notification for user
            create_notification(
                user=user,
                notification_type='bill_received',
                title=f'New Bill from {provider.provider_name}',
                message=f'You have received a new {bill.bill_type} bill for ${bill.amount}',
                related_bill=bill
            )
            
            messages.success(request, f"Bill sent to {user.username} successfully!")
            return redirect('provider_home')
    else:
        form = BillForm()
    
    return render(request, 'billing/send_bill.html', {
        'form': form,
        'user': user
    })

    # billing/views.py

@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check if user has permission to view this bill
    if not (request.user == bill.user or request.user.userprofile.provider == bill.provider):
        messages.error(request, "You don't have permission to view this bill.")
        return redirect('notifications')
        
    return render(request, 'billing/bill_detail.html', {
        'bill': bill
    })