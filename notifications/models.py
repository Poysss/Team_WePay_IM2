from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('bill_received', 'Bill Received'),
        ('payment_success', 'Payment Success'),
        ('payment_received', 'Payment Received'),
        ('bill_due', 'Bill Due Soon'),
        ('bill_overdue', 'Bill Overdue'),
        ('provider_added', 'Provider Added')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_bill = models.ForeignKey('billing.Bill', on_delete=models.SET_NULL, null=True, blank=True)
    related_payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def get_icon(self):
        icons = {
            'bill_received': 'file-text',
            'payment_success': 'check-circle',
            'payment_received': 'dollar-sign',
            'bill_due': 'clock',
            'bill_overdue': 'alert-circle',
            'provider_added': 'user-plus'
        }
        return icons.get(self.notification_type, 'bell')

    def get_color(self):
        colors = {
            'bill_received': 'blue',
            'payment_success': 'green',
            'payment_received': 'green',
            'bill_due': 'orange',
            'bill_overdue': 'red',
            'provider_added': 'purple'
        }
        return colors.get(self.notification_type, 'gray')