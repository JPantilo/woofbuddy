from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'method', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('transaction_id', 'appointment__user__username')
    readonly_fields = ('transaction_id', 'created_at')
