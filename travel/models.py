from django.db import models
from django.contrib.auth.models import User

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.destination} - {self.start_date} to {self.end_date}"

# Model for User Profile (Only keep this one)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)  # Keep full name
    dob = models.DateField(null=True, blank=True)  # Keep date of birth
    contact_number = models.CharField(max_length=15, blank=True)  # Keep contact number
    profile_picture = models.ImageField(upload_to="profile_pictures/", default="default.jpg", null=True, blank=True)
    bio = models.TextField(blank=True)  # Add bio field

    def __str__(self):
        return self.user.username


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    review_text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TripPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.city} ({self.start_date} - {self.end_date})"

class Question(models.Model):
    text = models.CharField(max_length=255)

    QUESTION_TYPE_CHOICES = [
        ('city', 'City'),
        ('days', 'Number of Days'),
        ('age_group', 'Age Group'),
        ('travel_companion', 'Travel Companion'),
        ('food_preference', 'Food Preference'),
        ('activity_type', 'Activity Preference'),
        ('place_type', 'Type of Places'),
        ('additional_notes', 'Additional Notes'),
        ('budget', 'Budget'),
    ]
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)

    options = models.JSONField(null=True, blank=True)  # For multiple choice buttons
    is_open_ended = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Optional enhancements
    placeholder = models.CharField(max_length=255, null=True, blank=True)
    depends_on = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    required_answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.text

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    session_key = models.CharField(max_length=40, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to '{self.question.text}'"
# models.py
from django.db import models

class Itinerary(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Itinerary for {self.user.username if self.user else 'Guest'}"

from django.db import models
from django.contrib.auth.models import User

class HotelBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotel_bookings")
    hotel_name = models.CharField(max_length=255)
    hotel_class = models.CharField(max_length=50, blank=True, null=True)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    rate_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reviews = models.TextField(blank=True, null=True)
    hotel_link = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.hotel_name

    class Meta:
        verbose_name = "Hotel Booking"
        verbose_name_plural = "Hotel Bookings"
