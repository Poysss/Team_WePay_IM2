from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    is_provider = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Provider(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=100)
    contact_info = models.TextField()

    def __str__(self):
        return self.provider_name