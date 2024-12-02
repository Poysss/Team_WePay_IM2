from django.db import models
from django.contrib.auth.models import User
from billing.models import Bill


class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('Gcash', 'Gcash'),
        ('Mastercard', 'Mastercard'),
        ('Paypal', 'Paypal'),
        ('Paymaya', 'Paymaya'),
        ('Visa', 'Visa'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.payment_type} (Balance: ${self.balance})"
    
class Payment(models.Model):
    PAYMENT_STATUS = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment for {self.bill.bill_type} - {self.bill.user.username}"