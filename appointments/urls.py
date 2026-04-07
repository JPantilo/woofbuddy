from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('history/', views.appointment_history, name='appointment_history'),
    path('admin/edit/<int:appointment_id>/', views.admin_edit_appointment, name='admin_edit_appointment'),
    path('admin/', views.admin_appointments, name='admin_appointments'),
    path('admin/history/', views.admin_appointment_history, name='admin_appointment_history'),
    path('pets/', views.pet_list, name='pet_list'),
    path('pets/add/', views.pet_create, name='pet_create'),
    path('pets/<int:pk>/edit/', views.pet_update, name='pet_update'),
    path('pets/<int:pk>/delete/', views.pet_delete, name='pet_delete'),
]
