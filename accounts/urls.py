# accounts/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='landing'), name='logout'),  # Updated this line
    path('register/', views.register_user, name='register_user'),
    path('register/provider/', views.register_provider, name='register_provider'),
    
    # User URLs
    path('user/home/', views.user_home, name='user_home'),
    path('user/profile/', views.profile_view, name='profile'),
    path('user/change-password/', views.change_password, name='change_password'),
    
    # Provider URLs
    path('provider/home/', views.provider_home, name='provider_home'),
    path('provider/profile/', views.provider_profile, name='provider_profile'),
]