from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('select/<int:appointment_id>/', views.select_payment_method, name='select_payment_method'),
    path('process/<int:appointment_id>/', views.process_payment, name='process_payment'),
    path('cash/<int:appointment_id>/', views.process_cash_payment, name='process_cash_payment'),
    path('invoice/<int:payment_id>/', views.cash_invoice, name='cash_invoice'),
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    path('paypal/create/<int:appointment_id>/', views.create_paypal_payment, name='create_paypal_payment'),
    path('paypal/return/', views.paypal_return, name='paypal_return'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
    path('paypal/notify/', views.paypal_notify, name='paypal_notify'),
]
