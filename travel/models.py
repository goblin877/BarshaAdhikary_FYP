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

# Model for Travel Guides (Optional, if you want to include travel guides)
class TravelGuide(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class TripPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.city} ({self.start_date} - {self.end_date})"
class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    booking_link = models.URLField()

    def __str__(self):
        return self.name

