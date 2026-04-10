from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import User
from .forms import CustomUserCreationForm
from .decorators import admin_required
from appointments.models import Appointment, Service, Pet
from appointments.notifications import send_appointment_approval_notification, send_appointment_cancellation
from payments.models import Payment

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    # Get user's appointments sorted by date and time
    user_appointments = request.user.appointments.all().order_by('date', 'time')
    
    context = {
        'user': request.user,
        'user_appointments': user_appointments,
    }
    return render(request, 'dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Woof Buddy.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@admin_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get statistics
    total_users = User.objects.filter(is_staff=False).count()
    total_services = Service.objects.filter(is_active=True).count()
    total_pets = Pet.objects.count()
    
    # Appointment statistics
    total_appointments = Appointment.objects.count()
    active_appointments = Appointment.objects.filter(status__in=['pending', 'approved']).count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
    
    # Revenue calculations
    completed_payments = Payment.objects.filter(status='completed')
    total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # PayPal vs Cash breakdown
    paypal_revenue = completed_payments.filter(method='paypal').aggregate(total=Sum('amount'))['total'] or 0
    cash_revenue = completed_payments.filter(method='cash').aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent activity
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.order_by('-created_at')[:5]
    recent_pets = Pet.objects.select_related('owner').order_by('-created_at')[:5]
    
    # Calculate average revenue per user
    avg_revenue_per_user = total_revenue / total_users if total_users > 0 else 0
    
    context = {
        'total_users': total_users,
        'total_appointments': total_appointments,
        'active_appointments': active_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_services': total_services,
        'total_pets': total_pets,
        'total_revenue': total_revenue,
        'paypal_revenue': paypal_revenue,
        'cash_revenue': cash_revenue,
        'avg_revenue_per_user': avg_revenue_per_user,
        'recent_appointments': recent_appointments,
        'recent_payments': recent_payments,
        'recent_pets': recent_pets,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@admin_required
def admin_pets(request):
    pets = Pet.objects.all().select_related('owner').order_by('-created_at')
    return render(request, 'admin_pets.html', {'pets': pets})

@login_required
def admin_users(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    users = User.objects.filter(is_staff=False)
    return render(request, 'admin_users.html', {'users': users})

@login_required
def admin_edit_user(request, user_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.address = request.POST.get('address')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()
        
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('admin_users')
    
    return render(request, 'admin_edit_user.html', {'user': user})

@login_required
def admin_user_details(request, user_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    # Get user's appointments
    appointments = Appointment.objects.filter(user=user).select_related('pet', 'service')
    
    # Get user's pets
    pets = user.pets.all()
    
    return render(request, 'admin_user_details.html', {
        'user': user,
        'appointments': appointments,
        'pets': pets
    })

@login_required
def admin_appointments(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointments = Appointment.objects.all().select_related('user', 'pet', 'service').order_by('-date', '-time')
    return render(request, 'admin_appointments.html', {'appointments': appointments})

@login_required
def admin_approve_appointment(request, appointment_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'approved'
    appointment.save()
    
    # Send approval notification to customer
    try:
        send_appointment_approval_notification(appointment)
        messages.success(request, f'Appointment for {appointment.pet.name} has been approved! Notification email sent.')
    except Exception as e:
        messages.success(request, f'Appointment for {appointment.pet.name} has been approved!')
        messages.warning(request, f'Email notification could not be sent: {e}')
    
    return redirect('admin_appointments')

@login_required
def admin_complete_appointment(request, appointment_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if payment is completed before allowing appointment completion
    # Exception: Allow completion if payment method is cash (pay at salon)
    if not appointment.payment:
        messages.error(request, 'Cannot complete appointment: No payment found. User must complete payment first.')
        return redirect('admin_appointments')
    
    if appointment.payment.status != 'completed' and appointment.payment.method != 'cash':
        messages.error(request, 'Cannot complete appointment: Payment is not completed. Please ensure payment is received first.')
        return redirect('admin_appointments')
    
    appointment.status = 'completed'
    appointment.save()
    
    messages.success(request, f'Appointment for {appointment.pet.name} has been marked as completed!')
    return redirect('admin_appointments')

@login_required
def admin_cancel_appointment(request, appointment_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'cancelled'
    appointment.save()
    
    # Send cancellation notification to customer
    try:
        send_appointment_cancellation(appointment)
        messages.warning(request, f'Appointment for {appointment.pet.name} has been cancelled! Notification email sent.')
    except Exception as e:
        messages.warning(request, f'Appointment for {appointment.pet.name} has been cancelled!')
        messages.warning(request, f'Email notification could not be sent: {e}')
    
    return redirect('admin_appointments')

@login_required
def admin_payments(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    payments = Payment.objects.all().select_related('appointment__user', 'appointment__pet', 'appointment__service').order_by('-created_at')
    return render(request, 'admin_payments.html', {'payments': payments})

@login_required
def admin_services(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    services = Service.objects.all().order_by('name')
    return render(request, 'admin_services.html', {'services': services})

@login_required
def admin_add_service(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_minutes = request.POST.get('duration_minutes')
        is_active = request.POST.get('is_active') == 'on'
        
        service = Service.objects.create(
            name=name,
            description=description,
            price=price,
            duration_minutes=duration_minutes,
            is_active=is_active
        )
        
        messages.success(request, f'Service "{service.name}" has been added successfully!')
        return redirect('admin_services')
    
    return render(request, 'admin_add_service.html')

@login_required
def admin_edit_service(request, service_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.duration_minutes = request.POST.get('duration_minutes')
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()
        
        messages.success(request, f'Service "{service.name}" has been updated successfully!')
        return redirect('admin_services')
    
    return render(request, 'admin_edit_service.html', {'service': service})

@login_required
def admin_activate_service(request, service_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = True
    service.save()
    
    messages.success(request, f'Service "{service.name}" has been activated!')
    return redirect('admin_services')

@login_required
def admin_deactivate_service(request, service_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = False
    service.save()
    
    messages.warning(request, f'Service "{service.name}" has been deactivated!')
    return redirect('admin_services')

@login_required
def admin_complete_cash_payment(request, payment_id):
    """Mark cash payment as completed (admin action)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.method == 'cash' and payment.status == 'pending':
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        messages.success(request, f'Cash payment for {payment.appointment.pet.name} has been marked as completed!')
    else:
        messages.error(request, 'This payment cannot be marked as completed.')
    
    return redirect('admin_payments')

@login_required
def admin_delete_service(request, service_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    service = get_object_or_404(Service, id=service_id)
    service_name = service.name
    service.delete()
    
    messages.error(request, f'Service "{service_name}" has been deleted!')
    return redirect('admin_services')
