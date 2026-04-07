from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ₱{self.price}"

class Pet(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    ]
    
    ANIMAL_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Rabbit', 'Rabbit'),
        ('Other', 'Other'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=20, choices=ANIMAL_CHOICES, default='Dog')
    breed = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    age_years = models.IntegerField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, help_text="Any allergies or medical conditions we should know about?")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.pet.name} - {self.service.name} on {self.date}"

# Calendar Management Models
class WorkingHours(models.Model):
    """Define working hours for the salon"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Working Hours"
    
    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.opening_time} - {self.closing_time}"

class TimeSlot(models.Model):
    """Manage available time slots for appointments"""
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    max_appointments = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

class BlockedTime(models.Model):
    """Block specific time slots (holidays, maintenance, etc.)"""
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}: {self.reason}"

class CalendarSettings(models.Model):
    """Global calendar settings"""
    appointment_duration = models.IntegerField(default=60, help_text="Duration in minutes")
    booking_advance_days = models.IntegerField(default=30, help_text="How many days in advance users can book")
    cancellation_cutoff_hours = models.IntegerField(default=24, help_text="Hours before appointment when cancellation is not allowed")
    auto_reminder_hours = models.IntegerField(default=24, help_text="Hours before appointment to send reminder")
    
    def __str__(self):
        return f"Calendar Settings"
    
    class Meta:
        verbose_name_plural = "Calendar Settings"
