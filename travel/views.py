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
import requests
from django.shortcuts import get_object_or_404, render
from .models import Trip

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
    
    # Fetch weather data from OpenWeatherMap API if latitude and longitude are available
    weather_info = None
    if trip.latitude and trip.longitude:
        weather_api_key = "ac7dfa82b795fc910c53c9999e427fca"  # Replace with your actual API key
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={trip.latitude}&lon={trip.longitude}&appid={weather_api_key}&units=metric"  # Add units=metric for temperature in Celsius
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            # Extract detailed weather info
            weather_description = weather_data.get("weather", [{}])[0].get("description", "No weather data available")
            temperature = weather_data.get("main", {}).get("temp", "No temperature data available")
            humidity = weather_data.get("main", {}).get("humidity", "No humidity data available")
            pressure = weather_data.get("main", {}).get("pressure", "No pressure data available")
            wind_speed = weather_data.get("wind", {}).get("speed", "No wind data available")

            # Prepare the weather info to pass to the template
            weather_info = {
                "description": weather_description,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "wind_speed": wind_speed
            }

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
        'weather_info': weather_info,  # Pass weather info to the template
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
from django.shortcuts import render
from django.http import JsonResponse

# Store API credentials directly (Not recommended for production)
CLIENT_ID = "mdWOlvVehsn6eJPLohv4f6gCAkgsX8Tb"
CLIENT_SECRET = "YxzJh4uQu8Cahvcz"

def get_amadeus_access_token():
    """Fetch Amadeus API access token."""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    print("Token Response:", response.json())  # Debugging line
    return response.json().get("access_token") if response.status_code == 200 else None

from .models import HotelStaticInfo  # Import the static hotel information

def get_hotels(request):
    """Fetch hotels from Amadeus API based on the destination input and add static data."""
    access_token = get_amadeus_access_token()
    if not access_token:
        return render(request, 'travel/hotel_search.html', {'error': 'Failed to obtain access token'})

    destination = request.GET.get('query', '').strip()
    if not destination:
        return render(request, 'travel/hotel_search.html', {'error': 'Please enter a destination'})

    # Fetch city data from Amadeus API
    url = 'https://test.api.amadeus.com/v1/reference-data/locations/cities'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'keyword': destination, 'max': 1}

    city_response = requests.get(url, headers=headers, params=params)

    if city_response.status_code == 200 and city_response.json().get('data'):
        city_code = city_response.json()['data'][0]['iataCode']
    else:
        return render(request, 'travel/hotel_search.html', {'error': 'Invalid destination'})

    # Fetch hotel data from Amadeus API
    hotel_url = 'https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city'
    hotel_params = {
        'cityCode': city_code,
        'radius': 5,
        'radiusUnit': 'KM',
        'hotelSource': 'ALL'
    }

    hotel_response = requests.get(hotel_url, headers=headers, params=hotel_params)

    if hotel_response.status_code == 200:
        hotels = hotel_response.json().get('data', [])[:5]  # Limit to first 5 hotels
        hotel_data = []

        # Fetch static data from the database (HotelStaticInfo)
        static_info_list = HotelStaticInfo.objects.all()[:5]  # Fetch the first 5 static info entries

        # Iterate over the hotels and static data
        for i, hotel in enumerate(hotels):
            address = hotel.get('address', {})
            address_line = address.get('lines', [None])[0] if address.get('lines') else None
            city_name = address.get('cityName', None)
            country = address.get('countryCode', None)

            # Set the address to a default string only if data is missing
            full_address = f"{address_line}, {city_name}, {country}" if address_line or city_name or country else "Address not available"

            # Check if there's corresponding static info for this hotel
            if i < len(static_info_list):
                static_info = static_info_list[i]
                image_url = static_info.image.url if static_info.image else None
                price = static_info.price
                rating = static_info.rating
                hotel_slot = dict(HotelStaticInfo.SLOT_CHOICES).get(static_info.hotel_slot, 'No Slot Info')  # Get slot display text
            else:
                image_url = None
                price = None
                rating = None
                hotel_slot = 'No Slot Info'

            hotel_data.append({
                'name': hotel['name'],
                'address': full_address,
                'city': city_name or 'Unknown City',  # Default to 'Unknown City' if not available
                'country': country or 'Unknown Country',  # Default to 'Unknown Country' if not available
                'image': hotel['media'][0]['uri'] if hotel.get('media') else image_url,  # Image from Amadeus API or local fallback
                'price': price,
                'rating': rating,  # Rating fetched from the static info model
                'hotel_slot': hotel_slot  # Adding the hotel slot info to display
            })

        return render(request, 'travel/hotel_search.html', {
            'hotels': hotel_data,
            'query': destination
        })

    return render(request, 'travel/hotel_search.html', {
        'error': 'Failed to fetch hotel data',
        'query': destination
    })

def hotel_search(request):
    return render(request, 'travel/hotel_search.html')

from django.shortcuts import render
import requests

def get_amadeus_access_token():
    """Fetch Amadeus API access token."""
    CLIENT_IDFLI = "IHUlkMee73a2QKKTp3YPXABhF6dRpKoj"
    CLIENT_SECRETFLI = "S0y9AbAxmM7q2kcL"

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_IDFLI,
        "client_secret": CLIENT_SECRETFLI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error fetching access token:", response.json())
        return None

def search_flights_page(request):
    """Handle flight search form and display results on the same page."""
    flights = None
    error = None
    
    if request.method == 'POST':
        access_token = get_amadeus_access_token()
        if not access_token:
            error = "Failed to get access token"
        else:
            # Get user inputs from the search form
            origin = request.POST.get('departureCity', 'LON')
            destination = request.POST.get('arrivalCity', 'NYC')
            departure_date = request.POST.get('departureDate', '2025-04-10')
            adults = request.POST.get('adults', 1)

            # Amadeus API request
            flight_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': adults
            }

            response = requests.get(flight_url, headers=headers, params=params)

            if response.status_code == 200:
                flight_data = response.json().get("data", [])
                filtered_flights = []
                for flight in flight_data:
                    itineraries = flight.get("itineraries", [])
                    if itineraries:
                        first_leg = itineraries[0].get("segments", [])[0]  # First segment
                        flight_details = {
                            "airline": first_leg.get("carrierCode"),
                            "flightNumber": first_leg.get("number"),
                            "departureTime": first_leg.get("departure", {}).get("at"),
                            "arrivalTime": first_leg.get("arrival", {}).get("at"),
                            "price": flight.get("price", {}).get("total", "N/A")
                        }
                        filtered_flights.append(flight_details)
                
                # Limit the number of flights to 8-10
                flights = filtered_flights[:10]  # This will limit the results to 10 flights
            else:
                error = "Failed to fetch flight data"

    return render(request, 'travel/flight_search.html', {'flights': flights, 'error': error})
