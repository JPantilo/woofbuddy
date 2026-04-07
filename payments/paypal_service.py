import paypalrestsdk
from django.conf import settings
from .models import Payment, Appointment

class PayPalService:
    def __init__(self):
        self.configure_paypal()
    
    def configure_paypal(self):
        """Configure PayPal SDK with sandbox credentials"""
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET
        })
    
    def create_payment(self, appointment):
        """Create a PayPal payment for an appointment"""
        try:
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'redirect_urls': {
                    'return_url': settings.PAYPAL_RETURN_URL,
                    'cancel_url': settings.PAYPAL_CANCEL_URL
                },
                'transactions': [{
                    'item_list': {
                        'items': [{
                            'name': appointment.service.name,
                            'sku': f"appointment-{appointment.id}",
                            'price': str(appointment.service.price),
                            'currency': 'PHP',
                            'quantity': 1
                        }]
                    },
                    'amount': {
                        'total': str(appointment.service.price),
                        'currency': 'PHP'
                    },
                    'description': f'Payment for {appointment.service.name} - {appointment.pet.name}'
                }]
            })
            
            if payment.create():
                # Create payment record in database
                db_payment = Payment.objects.create(
                    appointment=appointment,
                    amount=appointment.service.price,
                    method='paypal',
                    status='pending',
                    transaction_id=payment.id
                )
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'approval_url': payment.links[1].href,  # Approval link
                    'db_payment_id': db_payment.id
                }
            else:
                return {
                    'success': False,
                    'error': payment.error
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_payment(self, payment_id, payer_id):
        """Execute a PayPal payment after user approval"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({'payer_id': payer_id}):
                # Update payment record in database
                db_payment = Payment.objects.get(transaction_id=payment_id)
                db_payment.status = 'completed'
                db_payment.save()
                
                # Update appointment status
                appointment = db_payment.appointment
                if appointment.status == 'pending':
                    appointment.status = 'approved'
                appointment.save()
                
                return {
                    'success': True,
                    'payment': payment
                }
            else:
                return {
                    'success': False,
                    'error': payment.error
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_details(self, payment_id):
        """Get payment details from PayPal"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
