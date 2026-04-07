from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView

class AdminLoginView(LoginView):
    template_name = 'admin_login.html'
    redirect_authenticated_user = False
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_staff:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(self.request, 'Invalid credentials or insufficient privileges.')
            return self.form_invalid(form)

def custom_logout(request):
    logout(request)
    # Check if user was staff and redirect to admin login
    if hasattr(request, 'user') and hasattr(request.user, 'is_staff') and request.user.is_staff:
        messages.info(request, 'You have been logged out of the admin panel.')
        return redirect('admin_login')
    return redirect('home')

@login_required
def admin_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out of the admin panel.')
    return redirect('admin_login')
