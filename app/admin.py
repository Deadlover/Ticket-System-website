from django.contrib import admin
from .models import *



@admin.register(Seat_Class)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ['id','name','price']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['id','seat_number','seat_class']

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id','movie_name','movie_description','movie_startTime','is_available','released_date','movie_length']

@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ['id','movie','start_time','hall_no']

@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ['id','screening','user','booked_date','total_price']

@admin.register(SeatSelect)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ['id','seat','screening','user']

@admin.register(BookingDetail)
class BookingDetailAdmin(admin.ModelAdmin):
    list_display = ['id','seat',]