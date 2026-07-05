from django.test import TestCase
from core.forms import RoomBookingForm


class RoomBookingFormTests(TestCase):
    def test_form_includes_student_fields(self):
        form = RoomBookingForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('region', form.fields)
        self.assertIn('phone_number', form.fields)
        self.assertIn('email', form.fields)
