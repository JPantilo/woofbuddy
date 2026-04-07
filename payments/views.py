from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Payment
from appointments.models import Appointment
from appointments.notifications import send_payment_receipt
from .paypal_service import PayPalService
import uuid

@login_required
def process_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if hasattr(appointment, 'payment'):
        messages.info(request, 'Payment already processed for this appointment.')
        return redirect('payments:payment_receipt', payment_id=appointment.payment.id)
        
    if request.method == 'POST':
        # Simulate successful payment
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.service.price,
            method='credit_card',
            status='completed',
            transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            completed_at=timezone.now()
        )
        appointment.status = 'approved'
        appointment.save()
        
        # Send payment receipt email
        try:
            send_payment_receipt(payment)
            messages.success(request, 'Payment successful! Your appointment is confirmed. Receipt email sent.')
        except Exception as e:
            messages.success(request, 'Payment successful! Your appointment is confirmed.')
            messages.warning(request, f'Receipt email could not be sent: {e}')
        
        return redirect('payments:payment_receipt', payment_id=payment.id)
        
    return render(request, 'payments/process.html', {'appointment': appointment})

@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, appointment__user=request.user)
    return render(request, 'payments/receipt.html', {'payment': payment})

@login_required
def process_cash_payment(request, appointment_id):
    """Process cash payment and create invoice"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(appointment=appointment).first()
    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Create cash payment record
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.service.price,
            method='cash',
            status='pending',  # Pending until paid at salon
            transaction_id=f"CASH-{uuid.uuid4().hex[:8].upper()}"
        )
        
        # Update appointment status to approved (payment pending)
        appointment.status = 'approved'
        appointment.save()
        
        messages.success(request, 'Appointment confirmed! Please pay ₱{} when you arrive at Woof Buddy.'.format(appointment.service.price))
        return redirect('payments:cash_invoice', payment_id=payment.id)
    
    return render(request, 'payments/cash_payment.html', {'appointment': appointment})

@login_required
def cash_invoice(request, payment_id):
    """Show cash payment invoice"""
    payment = get_object_or_404(Payment, id=payment_id, appointment__user=request.user)
    return render(request, 'payments/cash_invoice.html', {'payment': payment})

@login_required
def select_payment_method(request, appointment_id):
    """Show payment method selection page"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(appointment=appointment).first()
    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('dashboard')
    
    return render(request, 'payments/select_payment_method.html', {'appointment': appointment})

@login_required
def create_paypal_payment(request, appointment_id):
    """Create a PayPal payment for an appointment"""
    if not hasattr(settings, 'PAYPAL_CLIENT_ID') or settings.PAYPAL_CLIENT_ID == 'YOUR_SANDBOX_CLIENT_ID':
        messages.error(request, 'PayPal is not configured. Please contact administrator.')
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(appointment=appointment).first()
    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('dashboard')
    
    paypal_service = PayPalService()
    result = paypal_service.create_payment(appointment)
    
    if result['success']:
        # Store payment ID in session for verification
        request.session['paypal_payment_id'] = result['payment_id']
        request.session['db_payment_id'] = result['db_payment_id']
        request.session['appointment_id'] = appointment_id
        
        # Redirect to PayPal for approval
        return redirect(result['approval_url'])
    else:
        messages.error(request, f'Failed to create PayPal payment: {result.get("error", "Unknown error")}')
        return redirect('dashboard')

@login_required
def paypal_return(request):
    """Handle PayPal return after payment approval"""
    payment_id = request.session.get('paypal_payment_id')
    db_payment_id = request.session.get('db_payment_id')
    appointment_id = request.session.get('appointment_id')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, 'Invalid payment return.')
        return redirect('dashboard')
    
    paypal_service = PayPalService()
    result = paypal_service.execute_payment(payment_id, payer_id)
    
    if result['success']:
        messages.success(request, 'Payment completed successfully! Your appointment has been confirmed.')
        
        # Clear session
        request.session.pop('paypal_payment_id', None)
        request.session.pop('db_payment_id', None)
        request.session.pop('appointment_id', None)
        
        return redirect('dashboard')
    else:
        messages.error(request, f'Payment execution failed: {result.get("error", "Unknown error")}')
        return redirect('dashboard')

@login_required
def paypal_cancel(request):
    """Handle PayPal cancellation"""
    # Clear session
    request.session.pop('paypal_payment_id', None)
    request.session.pop('db_payment_id', None)
    request.session.pop('appointment_id', None)
    
    messages.warning(request, 'Payment was cancelled. You can try again later.')
    return redirect('dashboard')

@login_required
def paypal_notify(request):
    """Handle PayPal IPN (Instant Payment Notification)"""
    # This is for server-to-server communication
    # You would verify the payment with PayPal here
    # For now, we'll just return a 200 OK response
    return render(request, 'payments/paypal_notify.html')
