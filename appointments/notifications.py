from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Appointment
from payments.models import Payment

def send_appointment_confirmation(appointment):
    """Send appointment confirmation email to customer"""
    subject = f'Appointment Confirmation - {appointment.service.name} for {appointment.pet.name}'
    
    context = {
        'appointment': appointment,
        'user': appointment.user,
        'pet': appointment.pet,
        'service': appointment.service,
    }
    
    html_message = render_to_string('emails/appointment_confirmation.html', context)
    text_message = render_to_string('emails/appointment_confirmation.txt', context)
    
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_payment_receipt(payment):
    """Send payment receipt email to customer"""
    subject = f'Payment Receipt - {payment.appointment.service.name} for {payment.appointment.pet.name}'
    
    context = {
        'payment': payment,
        'appointment': payment.appointment,
        'user': payment.appointment.user,
        'pet': payment.appointment.pet,
        'service': payment.appointment.service,
    }
    
    html_message = render_to_string('emails/payment_receipt.html', context)
    text_message = render_to_string('emails/payment_receipt.txt', context)
    
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payment.appointment.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_appointment_reminder(appointment):
    """Send appointment reminder email (24 hours before)"""
    subject = f'Reminder: Your appointment tomorrow - {appointment.service.name} for {appointment.pet.name}'
    
    context = {
        'appointment': appointment,
        'user': appointment.user,
        'pet': appointment.pet,
        'service': appointment.service,
    }
    
    html_message = render_to_string('emails/appointment_reminder.html', context)
    text_message = render_to_string('emails/appointment_reminder.txt', context)
    
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_appointment_cancellation(appointment):
    """Send appointment cancellation email to customer and admin"""
    subject = f'Appointment Cancelled - {appointment.service.name} for {appointment.pet.name}'
    
    context = {
        'appointment': appointment,
        'user': appointment.user,
        'pet': appointment.pet,
        'service': appointment.service,
    }
    
    html_message = render_to_string('emails/appointment_cancellation.html', context)
    text_message = render_to_string('emails/appointment_cancellation.txt', context)
    
    # Send to customer
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    # Send notification to admin
    admin_subject = f'Appointment Cancelled by Customer: {appointment.user.username}'
    admin_html_message = render_to_string('emails/admin_cancellation_notification.html', context)
    admin_text_message = render_to_string('emails/admin_cancellation_notification.txt', context)
    
    send_mail(
        subject=admin_subject,
        message=admin_text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=admin_html_message,
        fail_silently=False,
    )

def send_appointment_approval_notification(appointment):
    """Send notification when appointment is approved"""
    subject = f'Appointment Approved - {appointment.service.name} for {appointment.pet.name}'
    
    context = {
        'appointment': appointment,
        'user': appointment.user,
        'pet': appointment.pet,
        'service': appointment.service,
    }
    
    html_message = render_to_string('emails/appointment_approved.html', context)
    text_message = render_to_string('emails/appointment_approved.txt', context)
    
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def check_and_send_reminders():
    """Check for appointments in the next 24 hours and send reminders"""
    tomorrow = timezone.now() + timezone.timedelta(hours=24)
    
    # Find appointments scheduled for tomorrow
    upcoming_appointments = Appointment.objects.filter(
        date=tomorrow.date(),
        status='approved'
    )
    
    for appointment in upcoming_appointments:
        send_appointment_reminder(appointment)
    
    return f"Sent {len(upcoming_appointments)} reminders"
