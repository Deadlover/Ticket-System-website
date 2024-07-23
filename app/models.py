from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import uuid

class Seat_Class(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Seat(models.Model):
    seat_number = models.CharField(max_length=5)
    seat_class = models.ForeignKey(Seat_Class, on_delete=models.CASCADE, related_name='seats')

    def __str__(self):
        return f"{self.seat_class.name} Seat {self.seat_number}"

class Movie(models.Model):
    movie_name = models.CharField(max_length=255)
    movie_image = models.ImageField(upload_to="Movie_image/")
    movie_description = models.TextField()
    movie_startTime = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    released_date = models.DateField()
    movie_length = models.IntegerField(help_text="Length of the movie in minutes")

    @property
    def movie_endTime(self):
        """Calculate the end time of the movie based on the length."""
        return self.movie_startTime + timedelta(minutes=self.movie_length)

    def __str__(self):
        return self.movie_name

class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings')
    start_time = models.DateTimeField()
    hall_no = models.IntegerField()

    def __str__(self):
        return f"{self.movie.movie_name} at {self.start_time} in Hall {self.hall_no}"

class SeatBooking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='bookings')
    booked_date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(help_text="Total price for all booked seats")
    purchase_order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    paymentid = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking #{self.pk} by {self.user.username if self.user else 'Unknown User'}"

class BookingDetail(models.Model):
    booking = models.ForeignKey(SeatBooking, on_delete=models.CASCADE, related_name='details')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='booking_details')
    price = models.IntegerField(help_text="Price at the time of booking")

    def __str__(self):
        return f"{self.seat.seat_number} booked under {self.booking}"

    class Meta:
        unique_together = (('booking', 'seat'),)  # Ensure a seat is only booked once per booking


class SeatSelect(models.Model):
    locked = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seat_selections')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='selections')
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='seat_selections')
    selected_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('seat', 'screening')  # Ensures a seat can't be selected by multiple users for the same screening.

    def __str__(self):
        return f'{self.user.username} selected {self.seat} for {self.screening}'

    def is_selection_active(self):
        """Check if the seat selection is still active based on a predefined timeout."""
        # Assuming a 10-minute window for selection confirmation.
        selection_timeout = 10
        now = timezone.now()
        return now <= self.selected_at + timedelta(minutes=selection_timeout) and not self.locked
