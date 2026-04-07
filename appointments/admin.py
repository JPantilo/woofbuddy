from django.contrib import admin
from .models import Service, Pet, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'breed', 'age_years', 'created_at')
    list_filter = ('created_at', 'breed')
    search_fields = ('name', 'owner__username', 'owner__email', 'breed')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'pet', 'service', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'service', 'created_at')
    search_fields = ('user__username', 'pet__name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
