from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PaymentMethod, Payment
from billing.models import Bill
from .forms import PaymentMethodForm, CashInForm, MakePaymentForm
import uuid
from notifications.views import create_notification
from django.db import transaction

@login_required
def payment_options(request):
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            payment_method.save()
            messages.success(request, 'Payment method added successfully!')
            return redirect('payment_options')
    else:
        form = PaymentMethodForm()
    
    return render(request, 'payments/payment_options.html', {
        'payment_methods': payment_methods,
        'form': form
    })

@login_required
def cash_in(request, method_id):
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    if request.method == 'POST':
        form = CashInForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method.balance += amount
            payment_method.save()
            messages.success(request, f'Successfully added ${amount} to your {payment_method.payment_type} wallet')
            return redirect('payment_options')
    else:
        form = CashInForm()
    
    return render(request, 'payments/cash_in.html', {
        'form': form,
        'payment_method': payment_method
    })

@login_required
def make_payment(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    
    if bill.status == 'Paid':
        messages.error(request, 'This bill has already been paid.')
        return redirect('bill_history')
    
    if request.method == 'POST':
        form = MakePaymentForm(request.user, request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method.balance < bill.amount:
                messages.error(request, 'Insufficient balance in selected payment method.')
                return redirect('make_payment', bill_id=bill_id)
            
            try:
                with transaction.atomic():
                    # Create payment
                    payment = form.save(commit=False)
                    payment.bill = bill
                    payment.amount_paid = bill.amount
                    payment.status = 'Success'
                    payment.transaction_id = str(uuid.uuid4())
                    
                    # Update payment method balance
                    payment_method.balance -= bill.amount
                    payment_method.save()
                    
                    # Update bill status
                    bill.status = 'Paid'
                    bill.save()
                    
                    payment.save()
                    
                    # Create notifications
                    create_notification(
                        user=request.user,
                        notification_type='payment_success',
                        title='Payment Successful',
                        message=f'Your payment of ${payment.amount_paid} for {bill.bill_type} was successful.',
                        related_payment=payment,
                        related_bill=bill
                    )
                    
                    create_notification(
                        user=bill.provider.user_profile.user,
                        notification_type='payment_received',
                        title=f'Payment Received from {request.user.username}',
                        message=f'Payment of ${payment.amount_paid} received for {bill.bill_type}.',
                        related_payment=payment,
                        related_bill=bill
                    )
                    
                    messages.success(request, 'Payment successful!')
                    return redirect('payment_success', payment_id=payment.id)
                    
            except Exception as e:
                messages.error(request, 'An error occurred during payment processing. Please try again.')
                return redirect('make_payment', bill_id=bill_id)
    else:
        form = MakePaymentForm(request.user)
    
    return render(request, 'payments/make_payment.html', {
        'form': form,
        'bill': bill
    })

@login_required
def payment_success(request, payment_id):
    # Get the payment object and check permissions
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Ensure only the bill user or provider can view the success page
    if not (request.user == payment.bill.user or 
            (request.user.userprofile.is_provider and request.user.userprofile.provider == payment.bill.provider)):
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('home')
    
    context = {
        'payment': payment,
        'bill': payment.bill,
        'payment_method': payment.payment_method,
    }
    
    return render(request, 'payments/payment_success.html', context)

@login_required
def remove_payment_method(request, method_id):
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    if request.method == 'POST':
        payment_method.delete()
        messages.success(request, 'Payment method removed successfully.')
    return redirect('payment_options')


@login_required
def make_payment(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    
    if bill.status == 'Paid':
        messages.error(request, 'This bill has already been paid.')
        return redirect('bill_history')
    
    if request.method == 'POST':
        form = MakePaymentForm(request.user, request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method.balance < bill.amount:
                messages.error(request, 'Insufficient balance in selected payment method.')
                return redirect('make_payment', bill_id=bill_id)
            
            payment = form.save(commit=False)
            payment.bill = bill
            payment.amount_paid = bill.amount
            payment.status = 'Success'
            payment.transaction_id = str(uuid.uuid4())
            
            # Update payment method balance
            payment_method.balance -= bill.amount
            payment_method.save()
            
            # Update bill status
            bill.status = 'Paid'
            bill.save()
            
            payment.save()
            
            # Create notifications
            create_notification(
                user=request.user,
                notification_type='payment_success',
                title='Payment Successful',
                message=f'Your payment of ${payment.amount_paid} for {bill.bill_type} was successful.',
                related_payment=payment
            )
            
            create_notification(
                user=bill.provider.user_profile.user,
                notification_type='payment_success',
                title=f'Payment Received from {request.user.username}',
                message=f'Payment of ${payment.amount_paid} received for {bill.bill_type}.',
                related_payment=payment
            )
            
            messages.success(request, 'Payment successful!')
            return redirect('payment_success', payment_id=payment.id)
    else:
        form = MakePaymentForm(request.user)
    
    return render(request, 'payments/make_payment.html', {
        'form': form,
        'bill': bill
    })