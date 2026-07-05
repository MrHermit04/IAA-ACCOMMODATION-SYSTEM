from django import forms
from django.db.models import Count, F, Q
from .models import Booking, Room
SEMESTER_CHOICES = [
    ('Semester 1', 'Semester 1'),
    ('Semester 2', 'Semester 2'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

class RoomBookingForm(forms.ModelForm):
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    class Meta:
        model = Booking
        fields = [
            'room', 'semester', 'first_name', 'middle_name', 'last_name',
            'region', 'district', 'ward', 'gender', 'phone_number', 'email'
        ]
        widgets = {
            'room': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.annotate(
            occupancy_count=Count('bookings', filter=Q(bookings__status__in=['CONFIRMED', 'PENDING']))
        ).filter(capacity__gt=F('occupancy_count')).order_by('floor_number', 'room_number')

