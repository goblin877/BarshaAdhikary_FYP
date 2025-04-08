from django.contrib import admin
from .models import  Question, Trip, UserProfile, Review, TripPlan, Response, Itinerary

# Question Admin
admin.site.register(Question)

# Trip Admin
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'start_date', 'end_date', 'latitude', 'longitude')

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'dob', 'contact_number', 'profile_picture', 'bio')

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'rating', 'created_at', 'review_text')

# TripPlan Admin
@admin.register(TripPlan)
class TripPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'start_date', 'end_date')

# Response Admin
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'session_key', 'submitted_at')

# Itinerary Admin
@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved', 'created_at', 'content')

from django.contrib import admin
from .models import HotelBooking

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('hotel_name', 'user', 'hotel_class', 'overall_rating', 'rate_per_night', 'reviews', 'hotel_link', 'image_url')
    search_fields = ('hotel_name', 'user__username')
    list_filter = ('user', 'hotel_class')
