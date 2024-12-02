# dashboard/models.py

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Provider

class ProviderSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'provider']
        
    def __str__(self):
        return f"{self.user.username} - {self.provider.provider_name}"