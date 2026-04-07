from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Pet, Appointment
from .forms import AppointmentForm, PetForm
from .notifications import send_appointment_confirmation, send_appointment_approval_notification, send_appointment_cancellation

@login_required
def admin_appointments(request):
    """Admin appointment management - show only active appointments"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    # Only show pending and approved appointments
    appointments = Appointment.objects.filter(
        status__in=['pending', 'approved']
    ).order_by('date', 'time')
    
    return render(request, 'admin_appointments.html', {'appointments': appointments})

@login_required
def admin_appointment_history(request):
    """Admin appointment history - show completed and cancelled appointments"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    # Show completed and cancelled appointments
    appointments = Appointment.objects.filter(
        status__in=['completed', 'cancelled']
    ).order_by('-date', '-time')
    
    return render(request, 'admin_appointment_history.html', {'appointments': appointments})

@login_required
def admin_edit_appointment(request, appointment_id):
    """Edit an appointment (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('admin_appointments')
    else:
        form = AppointmentForm(request.user, instance=appointment)
    
    return render(request, 'appointments/admin_edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def appointment_history(request):
    """Show user's completed and cancelled appointment history"""
    appointments = Appointment.objects.filter(
        user=request.user,
        status__in=['completed', 'cancelled']
    ).order_by('-date', '-time')  # Most recent first
    
    # Calculate statistics
    completed_count = appointments.filter(status='completed').count()
    cancelled_count = appointments.filter(status='cancelled').count()
    
    return render(request, 'appointments/history.html', {
        'appointments': appointments,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
    })

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            
            # Send appointment confirmation email
            try:
                send_appointment_confirmation(appointment)
                messages.success(request, 'Appointment successfully created! Confirmation email sent.')
            except Exception as e:
                messages.success(request, 'Appointment successfully created! Please proceed to payment.')
                messages.warning(request, f'Email notification could not be sent: {e}')
            
            return redirect('payments:select_payment_method', appointment_id=appointment.id)
    else:
        # Check if user has pets
        if request.user.pets.count() == 0:
            messages.warning(request, 'You must add a pet before booking an appointment.')
            # To keep things simple we auto-create a default pet if none exists for this rewrite
            pet = Pet.objects.create(
                owner=request.user,
                name='Default Pet',
                animal_type='Dog',
                breed='Mixed',
                gender='U',
                age_years=1
            )
            messages.info(request, f'A default pet "{pet.name}" has been created for you.')
        
        # Check if services exist, if not create dummy ones
        if Service.objects.count() == 0:
            Service.objects.create(name="Full Grooming", description="Bath, haircut, nail trim", price=75.00)
            Service.objects.create(name="Bath and Brush", description="A simple wash and brush", price=45.00)
        
        # Pre-fill form with calendar selections
        initial_data = {}
        if 'date' in request.GET:
            initial_data['date'] = request.GET['date']
        if 'time' in request.GET:
            initial_data['time'] = request.GET['time']
            
        form = AppointmentForm(request.user, initial=initial_data)
        
    return render(request, 'appointments/book.html', {'form': form})

@login_required
def pet_list(request):
    pets = Pet.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'pets/list.html', {'pets': pets})

@login_required
def pet_create(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, f"{pet.name} has been added successfully!")
            return redirect('pet_list')
    else:
        form = PetForm()
    return render(request, 'pets/form.html', {'form': form, 'title': 'Add New Pet'})

@login_required
def pet_update(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f"{pet.name} has been updated successfully!")
            return redirect('pet_list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pets/form.html', {'form': form, 'title': f'Update {pet.name}', 'pet': pet})

@login_required
def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = pet.name
        pet.delete()
        messages.success(request, f"{name} has been removed.")
        return redirect('pet_list')
    return render(request, 'pets/confirm_delete.html', {'pet': pet})
