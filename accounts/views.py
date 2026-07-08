import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Count, Q
from core.models import Block, Room, Booking, Payment
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import RoomBookingForm
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

# 1. User Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# 2. User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# 3. User Logout View
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('login')
    return render(request, 'accounts/logout.html')

# 4. Dashboard View (Only accessible if logged in)
@login_required(login_url='login')
def dashboard_view(request):
    # This renders the main student/user portal
    return render(request, 'accounts/dashboard.html')

from django.db.models import F
from django.shortcuts import render
from core.models import Block,Room # Adjust according to your exact model name

def home_view(request):
    # Fetch available rooms from your database
    available_rooms = Room.objects.annotate(
        num_occupants=Count('bookings', filter=Q(bookings__status='active'))).filter(num_occupants__lt=F('capacity')).distinct().order_by('block', 'room_number')
    
    
    context = {
        'title': 'Welcome to the IAA Accommodation Portal',
        'rooms': available_rooms,
    }
    
    return render(request, 'core/home.html', context)

def room_list(request):
    rooms = Room.objects.all()
    rooms = sorted(
        rooms,
        key=lambda room: (
            room.floor_number,
            [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', str(room.room_number))]
        ),
    )
    paginator = Paginator(room_list, 50)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    form = RoomBookingForm()

    payment_info = None
    if request.user.is_authenticated:
        pending_booking = request.user.bookings.filter(status='PENDING').order_by('-booking_date').first()
        if pending_booking:
            payment_info = pending_booking.payments.order_by('-id').first()

    return render(request, 'core/rooms.html', {
        'rooms': rooms,
        'payment_info': payment_info,
        'form': form,
    })

@login_required
def my_bookings(request):
    bookings = request.user.bookings.all()
    return render(request, 'core/my_bookings.html', {'bookings' : bookings})

def contact(request) : 
    if request.method == 'POST' :
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        messages.success(request, 'Your message is successful received. Thanks')
    return render(request, 'core/contact.html')

@login_required
def apply_room_allocation(request):
    selected_room = None
    room_id = request.GET.get('room_id')
    
    # If room_id is provided in GET, pre-select it
    if room_id:
        try:
            selected_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            # Create a booking instance but do not save to DB yet
            booking = form.save(commit=False)
            booking.student = request.user  # Automatically assign the logged-in student
            booking.status = 'PENDING'     # Set default status
            booking.first_name = form.cleaned_data['first_name']
            booking.middle_name = form.cleaned_data['middle_name']
            booking.last_name = form.cleaned_data['last_name']
            booking.region = form.cleaned_data['region']
            booking.district = form.cleaned_data['district']
            booking.ward = form.cleaned_data['ward']
            booking.gender = form.cleaned_data['gender']
            booking.phone_number = form.cleaned_data['phone_number']
            booking.email = form.cleaned_data['email']

            try:
                booking.full_clean()
                booking.save()

                # Create a payment record and generate the control number
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.room.price_per_semester,
                    is_successful=False,
                )

                messages.success(request, "Booking completed successfully. Your payment control number has been generated.")
                return redirect('payment_details', booking_id=booking.id)

            except ValidationError as e:
                for error_msg in e.messages:
                    messages.error(request, error_msg)
    else:
        # Pre-fill form with selected room if provided
        initial_data = {'room': selected_room.id} if selected_room else {}
        form = RoomBookingForm(initial=initial_data)

    context = {'form': form, 'selected_room': selected_room}
    return render(request, 'core/apply_room.html', context)

@login_required
def payment_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    payment = booking.payments.order_by('-id').first()
    return render(request, 'core/payment_details.html', {
        'booking': booking,
        'payment': payment,
    })

@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    booking.delete()
    messages.success(request, 'Booking is successful cancelled')
    return redirect('rooms')

