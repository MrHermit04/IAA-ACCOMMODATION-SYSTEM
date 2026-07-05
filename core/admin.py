from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Block, Room, Booking, Payment

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender_category', 'floors', 'capacity_per_block', 'total_rooms')
    list_filter = ('gender_category',)
    search_fields = ('name',)

    def total_rooms(self, obj):
        return obj.rooms.count()
    total_rooms.short_description = 'Total Rooms'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number', 'get_block_name', 'floor_number', 'capacity', 
        'current_occupants', 'price_per_semester', 'is_full'
    )
    list_filter = ('block', 'floor_number', 'has_communal_ensuite', 'capacity')
    search_fields = ('room_number', 'block__name')
    readonly_fields = ('is_full', 'current_occupants')
    list_editable = ('price_per_semester', 'capacity')

    def get_block_name(self, obj):
        return obj.block.name
    get_block_name.short_description = 'Block'
    get_block_name.admin_order_field = 'block__name'

    def is_full_status(self, obj):
        if obj.is_full:
            return format_html('<span style="color: red; font-weight: bold;">Full</span>')
        return format_html('<span style="color: green;">Has Space</span>')
    is_full_status.short_description = 'Occupancy Status'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'get_room_number', 'get_block_name', 
        'semester', 'booking_date', 'status'
    )
    list_filter = ('status', 'semester', 'room__block')
    search_fields = ('student__username', 'student__email', 'room__room_number', 'semester')
    readonly_fields = ('booking_date',)
    autocomplete_fields = ('student', 'room')
    actions = ['mark_as_confirmed', 'mark_as_cancelled']

    def get_room_number(self, obj):
        return obj.room.room_number
    get_room_number.short_description = 'Room Number'
    get_room_number.admin_order_field = 'room__room_number'

    def get_block_name(self, obj):
        return obj.room.block.name
    get_block_name.short_description = 'Block'
    get_block_name.admin_order_field = 'room__block__name'

    @admin.action(description="Mark selected bookings as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')

    @admin.action(description="Mark selected bookings as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin) : 
    list_display = ('id', 'booking', 'control_number', 'amount', 'is_successful', 'transaction_date')
    list_filter = ('is_successful', 'transaction_date')
    search_fields = ('control_number', 'booking_id')
    readonly_fields = ('control_number', 'amount', 'transaction_date')
