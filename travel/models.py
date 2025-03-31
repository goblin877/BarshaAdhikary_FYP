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
class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)  # Rating out of 5
    image_url = models.URLField(blank=True)  # URL for the image
    booking_link = models.URLField(blank=True)

    def __str__(self):
        return self.name

class HotelStaticInfo(models.Model):
    SLOT_CHOICES = [
        ('slot_1', 'Best Hotel in the city'),
        ('slot_2', 'Best service Provided'),
        ('slot_3', 'Most Luxurious'),
        ('slot_4', 'Affordable Hotel Option'),
        ('slot_5', 'Best View'),
    ]

    hotel_slot = models.CharField(max_length=10, choices=SLOT_CHOICES)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)  # Changed to ImageField
    availability = models.BooleanField(default=True)

    def get_slot_title(self):
        return dict(self.SLOT_CHOICES).get(self.hotel_slot, 'Unknown Slot')

    def __str__(self):
        return f"Static Info for {self.get_slot_title()} - {'Available' if self.availability else 'Not Available'}"

class Question(models.Model):
    # The question text to ask the user
    text = models.CharField(max_length=255)

    # The category or type of question (this helps to group questions logically)
    QUESTION_TYPE_CHOICES = [
        ('city', 'City'),
        ('days', 'Number of Days'),
        ('age_group', 'Age Group'),
        ('travel_companion', 'Travel Companion'),
        ('food_preference', 'Food Preference'),
        ('activity_type', 'Activity Preference'),
        ('place_type', 'Type of Places'),
        ('additional_notes', 'Additional Notes'),
    ]
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)

    # If the question has predefined options, you can store them here (for multiple choice questions)
    options = models.JSONField(null=True, blank=True)  # Store options as a JSON array, e.g., ["Under 18", "18-30", "30-60", "Above 60"]

    # Whether the question allows open-ended answers
    is_open_ended = models.BooleanField(default=False)  # True if open-ended, False for predefined options

    # The order in which the question should appear (this controls the flow of questions)
    order = models.PositiveIntegerField(default=0)

    # This field indicates if the question is currently active or not
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text
