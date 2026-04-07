from django import forms
from .models import Appointment, Pet

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'service', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_staff:
            # For admin editing, allow all pets
            self.fields['pet'].queryset = Pet.objects.all()
        else:
            # For regular users, only show their own pets
            self.fields['pet'].queryset = Pet.objects.filter(owner=user)

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'animal_type', 'breed', 'gender', 'age_years', 'medical_conditions', 'notes']
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
