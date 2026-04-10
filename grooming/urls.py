from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from users.auth_views import custom_logout, admin_logout, AdminLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('register/', user_views.register, name='register'),
    path('admin-dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', user_views.admin_users, name='admin_users'),
    path('admin-pets/', user_views.admin_pets, name='admin_pets'),
    path('admin-edit-user/<int:user_id>/', user_views.admin_edit_user, name='admin_edit_user'),
    path('admin-user-details/<int:user_id>/', user_views.admin_user_details, name='admin_user_details'),
    path('admin-appointments/', user_views.admin_appointments, name='admin_appointments'),
    path('admin-approve-appointment/<int:appointment_id>/', user_views.admin_approve_appointment, name='admin_approve_appointment'),
    path('admin-complete-appointment/<int:appointment_id>/', user_views.admin_complete_appointment, name='admin_complete_appointment'),
    path('admin-cancel-appointment/<int:appointment_id>/', user_views.admin_cancel_appointment, name='admin_cancel_appointment'),
    path('admin-payments/', user_views.admin_payments, name='admin_payments'),
    path('admin-complete-cash-payment/<int:payment_id>/', user_views.admin_complete_cash_payment, name='admin_complete_cash_payment'),
    path('admin-services/', user_views.admin_services, name='admin_services'),
    path('admin-add-service/', user_views.admin_add_service, name='admin_add_service'),
    path('admin-edit-service/<int:service_id>/', user_views.admin_edit_service, name='admin_edit_service'),
    path('admin-activate-service/<int:service_id>/', user_views.admin_activate_service, name='admin_activate_service'),
    path('admin-deactivate-service/<int:service_id>/', user_views.admin_deactivate_service, name='admin_deactivate_service'),
    path('admin-delete-service/<int:service_id>/', user_views.admin_delete_service, name='admin_delete_service'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logout/', custom_logout, name='logout'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-logout/', admin_logout, name='admin_logout'),
    path('appointments/', include('appointments.urls')),
    path('payments/', include('payments.urls')),
    path('communications/', include('communications.urls')),
    path('create-admin/', user_views.create_admin_user, name='create_admin'),
]
