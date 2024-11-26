from django.db import models
from django.contrib.auth.models import User
from accounts.models import Provider

class Bill(models.Model):
    BILL_TYPES = [
        ('Electricity', 'Electricity'),
        ('Water', 'Water'),
        ('Internet', 'Internet'),
    ]
    
    BILL_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=BILL_STATUS, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill_type} - {self.user.username}"