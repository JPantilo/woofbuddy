from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment
from appointments.notifications import check_and_send_reminders

class Command(BaseCommand):
    help = 'Send appointment reminders for appointments in the next 24 hours'

    def handle(self, *args, **options):
        self.stdout.write('Checking for appointments to remind...')
        
        result = check_and_send_reminders()
        
        self.stdout.write(self.style.SUCCESS(f'Reminders sent: {result}'))
