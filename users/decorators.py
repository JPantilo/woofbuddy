from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

def admin_required(view_func):
    """Decorator to ensure user is logged in and is staff"""
    def check_user(user):
        return user.is_authenticated and user.is_staff
    
    decorated_view = user_passes_test(check_user, login_url='admin_login')(view_func)
    return decorated_view
