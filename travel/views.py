from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, TripForm, ProfileForm
from .models import TravelGuide, UserProfile, Trip
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from urllib.parse import quote
import requests
import hmac
import hashlib
import time
import requests
from django.http import JsonResponse
from .models import Trip
from datetime import date
from .models import TripPlan
from django.utils import timezone
import requests
from .models import Hotel
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse

UNSPLASH_ACCESS_KEY = "a8F8irghpyAE0DS4Wp602aus2Pci7-I5UoTA_aJgSU8"

# API credentials
API_KEY = '4cd60a8ccc51377e38c59a30439dabec'
API_SECRET = '8e4622e2e3'

# Homepage view
def home(request):
    if request.user.is_authenticated:
        context = {
            'is_authenticated': True,
            'username': request.user.username,
        }
    else:
        context = {
            'is_authenticated': False,
        }
    return render(request, 'travel/home.html', context)

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'travel/login.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Account created successfully! Welcome, {username}.")
                return redirect('home')
            else:
                messages.error(request, "Authentication failed. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'travel/signup.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# Profile view
@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_trips = Trip.objects.filter(user=request.user)  # Fetch user's trips

    return render(request, 'travel/profile.html', {"user_profile": user_profile, "user_trips": user_trips})
@login_required
def edit_profile(request):
    # Get or create the UserProfile instance for the logged-in user
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Use ProfileForm to handle form submission
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()  # Save the updated profile data
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, "travel/edit_profile.html", {"form": form})
# Plan Trip view
@login_required
def plan_trip(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Convert start_date and end_date to date objects
        start_date = date.fromisoformat(start_date)  # Assuming the format is YYYY-MM-DD
        end_date = date.fromisoformat(end_date)
        
        # Validate the dates
        today = date.today()
        if start_date < today:
            messages.error(request, "The start date cannot be in the past.")
            return render(request, 'travel/plan_trip.html')
        if end_date <= start_date:
            messages.error(request, "The end date must be after the start date.")
            return render(request, 'travel/plan_trip.html')
        
        # Save the trip plan
        trip = Trip.objects.create(
            user=request.user,
            destination=city,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, 'Trip plan saved successfully!')
        return redirect('profile')  # Redirect to profile after saving
        
    return render(request, 'travel/plan_trip.html')
# Profile view
@login_required
def profile_view(request):
    # Fetch trips for the logged-in user
    trips = Trip.objects.filter(user=request.user)

    # Fetch or create user profile for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)  

    return render(request, 'travel/profile.html', {
        'trips': trips,  # Passing saved trips to the template
        'user_profile': user_profile  # Passing edited profile data (including profile picture)
    })
# Guide view
def guide_view(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        TravelGuide.objects.create(title=title, description=description)
        return redirect('guide')

    guides = TravelGuide.objects.all()
    return render(request, 'travel/guide.html', {'guides': guides})

# About view
def about(request):
    return render(request, 'travel/about.html')

# Contact view
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send the email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_mail(
                f"Message from {name} ({email})",
                message,
                email,
                [settings.CONTACT_EMAIL],  # Define a contact email in settings.py
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # Redirect back to the contact page after submission
    else:
        form = ContactForm()

    return render(request, 'travel/contact.html', {'form': form})

# Trip details view
def trip_details(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)  # Get the trip object using trip_id
    
    # If latitude and longitude are not set, get them from an external API
    if not trip.latitude or not trip.longitude:
        geonames_url = f"http://api.geonames.org/searchJSON?name={trip.destination}&maxRows=1&username=Barsha1"
        response = requests.get(geonames_url)
        
        if response.status_code == 200:
            data = response.json()
            if data["geonames"]:
                trip.latitude = data["geonames"][0]["lat"]
                trip.longitude = data["geonames"][0]["lng"]
                trip.save()  # Save the trip with latitude and longitude if they are missing
        else:
            trip.latitude = None
            trip.longitude = None
    
    # Fetch images from Unsplash API
    unsplash_url = f"https://api.unsplash.com/search/photos?query={trip.destination}&client_id=a8F8irghpyAE0DS4Wp602aus2Pci7-I5UoTA_aJgSU8"
    response = requests.get(unsplash_url)
    
    if response.status_code == 200:
        images = response.json().get("results", [])
    else:
        images = []

    return render(request, 'travel/trip_details.html', {
        'trip': trip,
        'images': images,
    })
# Booking view
def booking_view(request):
    return render(request, 'travel/booking.html')

# Itinerary view
def itinerary(request):
    return render(request, 'travel/itinerary.html')

# Get city suggestions via API (for autofill)
def get_city_suggestions(request):
    query = request.GET.get("query", "")
    if query:
        username = "barsha1"  # Your GeoNames username
        url = f"http://api.geonames.org/searchJSON?name_startsWith={query}&maxRows=10&username={username}&featureClass=P"
        response = requests.get(url)
        data = response.json()
        cities = [item["name"] for item in data.get("geonames", [])]
        return JsonResponse({"cities": cities})
    return JsonResponse({"cities": []})

@login_required
def delete_trip(request, id):  # 'id' matches the URL pattern
    trip = get_object_or_404(Trip, id=id, user=request.user)
    trip.delete()
    messages.success(request, "Trip deleted successfully!")
    return redirect('profile')  # Redirect to profile page

def load_more_images(request, trip_id):
    # Example logic to get more images using Unsplash API
    trip = Trip.objects.get(id=trip_id)  # Get trip instance if needed

    # Example of fetching more images from Unsplash API
    unsplash_url = f"https://api.unsplash.com/photos?page=2&client_id=a8F8irghpyAE0DS4Wp602aus2Pci7-I5UoTA_aJgSU8"
    response = requests.get(unsplash_url)
    images = response.json()

    # Prepare the images for returning
    image_data = [{'url': image['urls']['regular'], 'alt_description': image['alt_description']} for image in images]
    
    return JsonResponse({'images': image_data})
def generate_signature(api_key, api_secret, url, method, body=""):
    timestamp = str(int(time.time()))  # Current timestamp
    message = f"{method} {url} {api_key} {api_secret} {timestamp} {body}"
    
    # Generate HMAC-SHA256 hash
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    
    return signature


def hotel_search(request):
    query = request.GET.get('query', 'Paris')  # Get the search query (default to 'Paris')
    check_in_date = request.GET.get('check_in', '2025-03-11')  # Default check-in date
    check_out_date = request.GET.get('check_out', '2025-03-18')  # Default check-out date

    # Define the API URL and parameters
    url = f'https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels'
    headers = {
        'x-rapidapi-host': 'tripadvisor16.p.rapidapi.com',
        'x-rapidapi-key': '013c0f53c1msh6647f1c15c03db0p1c0739jsncfa956be7c4d'  # Replace with your API key
    }
    params = {
        'geoId': query,  # Destination name or geoId (e.g., Paris)
        'checkIn': check_in_date,
        'checkOut': check_out_date,
        'pageNumber': 1,
        'currencyCode': 'USD'
    }

    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Check for any HTTP errors
        hotels_data = response.json()
        
        # Extract hotel information from the API response
        hotels = hotels_data.get('data', [])
        
    except requests.exceptions.RequestException as e:
        # Handle any errors in the request
        hotels = []
        print(f"Error fetching data: {e}")

    return render(request, 'travel/hotel_search.html', {
        'hotels': hotels,
        'query': query,
        'check_in': check_in_date,
        'check_out': check_out_date
    })
def flight_info(request):
    if request.method == 'GET':
        # You can add flight search parameters here similar to hotel search
        flight_origin = request.GET.get('flight_origin')
        flight_destination = request.GET.get('flight_destination')
        flight_date = request.GET.get('flight_date')

        # Call to your flight API or logic to fetch flight info goes here...

    return render(request, 'travel/flight_info.html')  # Adjust this as needed

import requests
from django.http import JsonResponse

# Amadeus API credentials (store these securely, e.g., in environment variables)
CLIENT_ID = "mdWOlvVehsn6eJPLohv4f6gCAkgsX8Tb"
CLIENT_SECRET = "YxzJh4uQu8Cahvcz"

def get_amadeus_access_token():
    """Fetches the access token from Amadeus API"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

def fetch_hotels(request):
    """Fetches hotels using Amadeus API"""
    access_token = get_amadeus_access_token()
    if not access_token:
        return JsonResponse({"error": "Failed to obtain access token"}, status=400)

    # Example: Searching hotels in a city (replace with actual query parameters)
    hotel_search_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    params = {
        "cityCode": "PAR",  # Change this to the required city
        "radius": "10",
        "radiusUnit": "KM"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(hotel_search_url, params=params, headers=headers)
    
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch hotels"}, status=response.status_code)

# Function to get hotel data from Amadeus
def get_hotels(request):
    access_token = get_amadeus_access_token()
    if not access_token:
        return render(request, 'hotel_search.html', {'error': 'Failed to obtain access token'})

    destination = request.GET.get('query', 'PAR')  # Get city code from user input

    url = 'https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'cityCode': destination,
        'radius': 5,
        'radiusUnit': 'KM',
        'hotelSource': 'ALL'
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        hotels = response.json().get('data', [])
        hotel_data = []

        for hotel in hotels:
            address = hotel.get('address', {})
            address_line = address.get('lines', [None])[0]  # Safely get address
            
            hotel_data.append({
                'name': hotel['name'],
                'address': address_line,
                'city': address.get('cityName', ''),
                'country': address.get('countryCode', ''),
                'image': hotel['media'][0]['uri'] if hotel.get('media') else None
            })

        return render(request, 'hotel_search.html', {
            'hotels': hotel_data,
            'query': destination
        })
    
    else:
        return render(request, 'travel/hotel_search.html', {
            'error': 'Failed to fetch hotel data',
            'query': destination
        })