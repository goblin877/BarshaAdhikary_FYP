from django.contrib import admin
from .models import Hotel, HotelStaticInfo  # Importing Hotel and HotelStaticInfo

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'price', 'rating', 'image_url', 'booking_link')

@admin.register(HotelStaticInfo)
class HotelStaticInfoAdmin(admin.ModelAdmin):
    list_display = ('hotel_slot', 'price', 'rating', 'image', 'availability')  # Updated to use 'image' instead of 'image_url'
