from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import datetime


class Block(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    name = models.CharField(max_length=50)
    gender_category = models.CharField(max_length=1, choices=GENDER_CHOICES)
    floors = models.PositiveIntegerField(default=7)
    capacity_per_block = models.PositiveIntegerField(default=250)

    def __str__(self):
        return self.name

class Room(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    floor_number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField(default=6)
    price_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=200000.00)
    has_communal_ensuite = models.BooleanField(default=True)

    def clean(self):
        if self.floor_number > self.block.floors:
            raise ValidationError("Floor number cannot exceed the block's maximum floors.")
        super().clean()

    @property
    def is_full(self):
        return self.current_occupants >= self.capacity

    @property
    def current_occupants(self):
        return self.bookings.filter(status__in=['CONFIRMED', 'PENDING']).count()

    @property
    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0
        return int((self.current_occupants / self.capacity) * 100)

    @property
    def status_badge(self):
        if self.is_full:
            return 'FULL'
        elif self.current_occupants >= self.capacity * 0.75:
            return 'LIMITED'
        else:
            return 'AVAILABLE'

    @property
    def primary_color(self):
        """Return primary gradient color based on occupancy status"""
        if self.is_full:
            return '#ff6b6b'
        elif self.current_occupants >= self.capacity * 0.75:
            return '#ff9800'
        else:
            return '#4CAF50'

    @property
    def secondary_color(self):
        """Return secondary gradient color based on occupancy status"""
        if self.is_full:
            return '#ee5a6f'
        elif self.current_occupants >= self.capacity * 0.75:
            return '#e68900'
        else:
            return '#45a049'

    def __str__(self):
        return f"{self.block.name} - Room {self.room_number}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    semester = models.CharField(max_length=50) # e.g., "Semester 1"
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        if not self.pk: # If the booking is new
            if self.room.is_full:
                raise ValidationError("This room is already fully booked.")
        super().save(*args, **kwargs)

    def __str__(self):
        student_name = self.student.username if self.student else "Guest"
        room_number = self.room.room_number if self.room else "No Room"
        return f"Booking for {self.student.username} in Room {self.room.room_number}"

    def process_payment(self):
        """Actionable method to confirm booking after student payment."""
        if self.status == 'PENDING':
            # Check if a successful payment exists for this booking
            payment = self.payments.filter(is_successful=True).first()
            if payment:
                self.status = 'CONFIRMED'
                self.save()
                return True
        return False

class Payment(models.Model):
    """
    Model to track billing control numbers and transactions. 
    In Tanzania, this connects to institutional billing systems (e.g., GePG).
    """
    user = models.Foreignkey('auth.User', on_delete=models.CASCADE , null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    control_number = models.CharField(max_length=20, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_successful = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        user_name = self.user.username if self.user else "No User"
        return f"{user_name} - {self.control_number} - TZS {self.amount}"

    def generate_control_number(self):
        """
        Generates a unique control number. 
        In production, this should perform an API request to your central payment gateway 
        (e.g., Tanzania's [GePG Portal](https://billing.gepg.go.tz/)).
        """
        # Example: generates a 12-digit mock control number (YYYY + random suffix)
        year_prefix = datetime.datetime.now().strftime("%Y")
        unique_suffix = str(uuid.uuid4().int)[:8]
        return f"{year_prefix}{unique_suffix}"

    def save(self, *args, **kwargs):
        if not self.control_number:
            self.control_number = self.generate_control_number()
            # Set the exact amount from the room's pricing
            self.amount = self.booking.room.price_per_semester
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Control Number: {self.control_number} - Booking {self.booking.id}"
