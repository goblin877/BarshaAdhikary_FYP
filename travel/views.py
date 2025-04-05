from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from .forms import CustomUserCreationForm, TripForm, ProfileForm
from .models import UserProfile, Trip
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

def home(request):
    # Initialize context for unauthenticated users
    context = {'is_authenticated': request.user.is_authenticated}

    if request.user.is_authenticated:
        # Fetch the upcoming trips for the user, ordered by start date
        upcoming_trips = Trip.objects.filter(user=request.user, start_date__gte=datetime.now()).order_by('start_date')[:2]
        context.update({
            'username': request.user.username,
            'upcoming_trips': upcoming_trips,
        })

    # Fetch all reviews to be displayed on the homepage, ordered by most recent
    reviews = Review.objects.all().order_by('-created_at')[:4]  # Fetch the 4 most recent reviews
    context['reviews'] = reviews

    # Determine which template to render
    if request.user.is_authenticated:
        return render(request, 'travel/home.html', context)  # Show personalized homepage
    else:
        return render(request, 'travel/landing_page.html', context)  # Show landing page for unauthenticated users

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
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Trip, Itinerary

@login_required
def profile(request):
    # Fetch or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Fetch user trips ordered by start_date
    user_trips = Trip.objects.filter(user=request.user).order_by('start_date')

    # Fetch user itineraries
    itineraries = Itinerary.objects.filter(user=request.user)

    # Pass the user profile, trips, and itineraries to the template
    return render(request, 'travel/profile.html', {
        'user_profile': user_profile,
        'user_trips': user_trips,
        'itineraries': itineraries  # Adding itineraries
    })


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
"""@login_required
def profile_view(request):
    # Fetch trips for the logged-in user
    trips = Trip.objects.filter(user=request.user)

    # Fetch or create user profile for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)  

    return render(request, 'travel/profile.html', {
        'trips': trips,  # Passing saved trips to the template
        'user_profile': user_profile  # Passing edited profile data (including profile picture)
    })"""
# Guide view
from .models import Review
from .forms import ReviewForm
def guide_view(request):   
    reviews = Review.objects.all().order_by('-created_at')  # Fetch all reviews
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user  # Assign the logged-in user
            review.save()
            return redirect('guide')  # Redirect to refresh the page

    return render(request, 'travel/guide.html', {'form': form, 'reviews': reviews})

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
from datetime import timedelta

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
    
    # Fetch today's weather data from OpenWeatherMap API
    weather_info = None
    if trip.latitude and trip.longitude:
        weather_api_key = "ac7dfa82b795fc910c53c9999e427fca"  # Replace with your actual API key
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={trip.latitude}&lon={trip.longitude}&appid={weather_api_key}&units=metric"
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            weather_info = {
                "description": weather_data.get("weather", [{}])[0].get("description", "No weather data available"),
                "temperature": weather_data.get("main", {}).get("temp", "No temperature data available"),
                "humidity": weather_data.get("main", {}).get("humidity", "No humidity data available"),
                "pressure": weather_data.get("main", {}).get("pressure", "No pressure data available"),
                "wind_speed": weather_data.get("wind", {}).get("speed", "No wind data available")
            }

    # Fetch trip days' weather (based on trip start and end dates)
    trip_weather = []
    if trip.start_date and trip.end_date:
        # Generate a list of dates between start and end date
        date_range = [trip.start_date + timedelta(days=i) for i in range((trip.end_date - trip.start_date).days + 1)]
        
        for date in date_range:
            weather_url_trip = f"http://api.openweathermap.org/data/2.5/forecast?lat={trip.latitude}&lon={trip.longitude}&appid={weather_api_key}&units=metric&cnt=8"  # cnt=8 gives weather for the day at every 3-hour interval
            weather_response_trip = requests.get(weather_url_trip)
            
            if weather_response_trip.status_code == 200:
                weather_data_trip = weather_response_trip.json()
                # Filter weather data for the current date
                for entry in weather_data_trip.get("list", []):
                    # Check if the entry matches the date of the trip day
                    weather_date = entry["dt_txt"].split(" ")[0]
                    if weather_date == date.strftime("%Y-%m-%d"):
                        trip_weather.append({
                            "date": date,
                            "description": entry["weather"][0]["description"],
                            "temperature": entry["main"]["temp"],
                        })
                        break

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
        'weather_info': weather_info,
        'trip_weather': trip_weather,  # Pass weather info for trip days
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

from django.shortcuts import render
import requests

def get_amadeus_access_token():
    # Fetch Amadeus API access token.
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

def get_location_code(city_name, access_token):
    # Use Amadeus API to get location data (airport codes) based on city names
    location_url = f"https://test.api.amadeus.com/v1/reference-data/locations"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'keyword': city_name, 'subType': 'CITY'}

    response = requests.get(location_url, headers=headers, params=params)

    if response.status_code == 200:
        location_data = response.json().get('data', [])
        if location_data:
            # Return the first match's IATA code (airport code)
            return location_data[0].get('iataCode')
    return None

def search_flights_page(request):
    # Handle flight search form and display results on the same page.
    flights = None
    error = None
    
    if request.method == 'POST':
        access_token = get_amadeus_access_token()
        if not access_token:
            error = "Failed to get access token"
        else:
            # Get user inputs from the search form
            origin_city = request.POST.get('departureCity', 'London')
            destination_city = request.POST.get('arrivalCity', 'New York')
            departure_date = request.POST.get('departureDate', '2025-04-10')

            # Get location codes for both origin and destination city names
            origin = get_location_code(origin_city, access_token)
            destination = get_location_code(destination_city, access_token)

            if not origin or not destination:
                error = "Unable to resolve city names to airport codes"
            else:
                # Amadeus API request to get flights
                flight_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
                headers = {'Authorization': f'Bearer {access_token}'}
                params = {
                    'originLocationCode': origin,
                    'destinationLocationCode': destination,
                    'departureDate': departure_date,
                    'adults': 1  # Fixed to 1 as passengers field is removed
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
                                "price": flight.get("price", {}).get("total", "N/A"),
                                "departureCity": origin_city,  # Using user input
                                "arrivalCity": destination_city  # Using user input
                            }
                            filtered_flights.append(flight_details)

                    # Limit the number of flights to 8-10
                    flights = filtered_flights[:10]
                else:
                    error = "Failed to fetch flight data"

    return render(request, 'travel/flight_search.html', {'flights': flights, 'error': error})

from django.shortcuts import render, redirect
from django.http import HttpResponse

def flight_booking(request):
    if request.method == 'POST':
        flight = {
            'airline': request.POST['airline'],
            'flightNumber': request.POST['flightNumber'],
            'departureTime': request.POST['departureTime'],
            'arrivalTime': request.POST['arrivalTime'],
            'price': request.POST['price'],
            'departureCity': request.POST['departureCity'],
            'arrivalCity': request.POST['arrivalCity'],
        }

        # Store the flight details in the session
        request.session['selected_flight'] = flight

        # Redirect to the flight_search page to display the selected flight
        return redirect('flight_booking')


    return render(request, 'travel/flight_booking.html')
from django.shortcuts import render

def payment_view(request):
    # Your payment logic here
    return render(request, 'travel/payment.html')

def payment_process(request):
    if request.method == "POST":
        # Example: Get the payment form data
        card_number = request.POST.get('cardNumber')
        expiry_date = request.POST.get('expiryDate')
        cvv = request.POST.get('cvv')

        # Add logic to process the payment (e.g., payment gateway integration)

        # Redirect to a success page (or handle error as needed)
        return redirect('payment_success')  # Ensure you have a 'payment_success' view

    # If method is not POST, you could redirect back to the payment page or handle it otherwise
    return redirect('payment')  # Assuming you want to redirect back to the payment page

from django.shortcuts import render
def hotel_booking(request):
    return render(request, 'travel/hotel_booking.html')  # Render the hotel_booking.html template

import requests
from django.shortcuts import render

def get_hotels(request):
    """Fetch hotels from SerpAPI based on the destination input."""
    destination = request.GET.get('query', '').strip()
    
    if not destination:
        return render(request, 'travel/hotel_search.html', {'error': 'Please enter a destination'})

    # SerpAPI endpoint and API key
    API_KEY = "7ba5ac77812e54a4d20e05560195047deffa3494fd7b259bffa8d01bdce4e088"  # Replace with your actual SerpAPI key
    url = f"https://serpapi.com/search?q=hotels+in+{destination}&location={destination}&api_key={API_KEY}"

    # Fetch hotel data from SerpAPI
    response = requests.get(url)
    
    if response.status_code == 200:
        # Extract hotel data from the JSON response
        data = response.json()
        
        # If there are hotels in the response
        if 'hotels' in data:
            hotels = data['hotels']
        else:
            return render(request, 'travel/hotel_search.html', {'error': 'No hotels found for this destination'})
        
    else:
        return render(request, 'travel/hotel_search.html', {'error': 'Failed to fetch hotel data'})

    # Process the hotel data
    hotel_data = []
    for hotel in hotels:
        hotel_data.append({
            'name': hotel.get('name', 'N/A'),
            'address': hotel.get('address', 'No Address Available'),
            'price': hotel.get('price', 'N/A'),
            'rating': hotel.get('rating', 'N/A'),
            'image': hotel.get('image', 'https://via.placeholder.com/300'),
        })

    return render(request, 'travel/hotel_search.html', {'hotels': hotel_data, 'query': destination})


from django.shortcuts import render
import requests

def fetch_hotels(request):
    # Get user input from query parameters
    city = request.GET.get("city", "Pokhara")  # Default to 'Pokhara' if not provided
    check_in_date = request.GET.get("check_in_date", "2025-04-01")  # Default check-in date
    check_out_date = request.GET.get("check_out_date", "2025-04-05")  # Default check-out date
    
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {city}",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "USD",
        "api_key": "7ba5ac77812e54a4d20e05560195047deffa3494fd7b259bffa8d01bdce4e088",  # Replace with your actual API key
    }

    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code == 200:
        data = response.json()

        formatted_hotels = []
        for idx, hotel in enumerate(data.get("properties", [])):  # Use index to create unique 'id'
            formatted_hotels.append({
                "id": idx,  # Add a unique 'id' based on the index
                "name": hotel.get("name"),
                "description": hotel.get("description"),
                "link": hotel.get("link"),
                "rate_per_night": hotel.get("rate_per_night", {}).get("lowest"),
                "hotel_class": hotel.get("hotel_class"),
                "overall_rating": hotel.get("overall_rating"),
                "reviews": hotel.get("reviews"),
                "images": [image.get("original_image") for image in hotel.get("images", [])]
            })

        return render(request, "travel/hotel_booking.html", {"hotels": formatted_hotels})

    else:
        return JsonResponse({"error": "Failed to fetch hotels", "details": response.text}, status=response.status_code)

import stripe
from django.http import JsonResponse
from django.shortcuts import render

# Define your API keys directly in views.py (Not recommended for production)
STRIPE_PUBLIC_KEY = "pk_test_51R6BtY02ZhWfahdvnPETt1gzaUiJf3yW3N7hioxaYvW7xVIQUvgO3p2wRAxgLMnXSwKsCXb1uLF9nXVdhuqmprMN00vxQvPQ1I"
STRIPE_SECRET_KEY = "sk_test_51R6BtY02ZhWfahdvq63bGLYgvE0qx0TN6X75aElMc8T0zMew6jaIFpSuDwuWA6PBEM1gbFasZQ6wJA3GesSRm5lf00PQuprbml"

stripe.api_key = STRIPE_SECRET_KEY  # Set the secret key for API calls

def book_hotel(request, hotel_id=None):  
    hotel = {
        'name': request.GET.get('name', 'Unknown Hotel'),
        'hotel_class': request.GET.get('class', 'N/A'),
        'overall_rating': request.GET.get('rating', 'N/A'),
        'description': request.GET.get('description', 'No description available.'),
        'rate_per_night': request.GET.get('price', 'N/A'),
        'reviews': request.GET.get('reviews', 'N/A'),
        'link': request.GET.get('link', '#'),
        'image': request.GET.get('image', ''),
    }
    return render(request, 'travel/book_hotel.html', {'hotel': hotel, 'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY})

def create_checkout_session(request):
    print("Creating checkout session...")  # Log when the session creation is called

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Booking Payment'},
                'unit_amount': 1000,  # Amount in cents ($10)
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url="http://127.0.0.1:8000/success/",
        cancel_url="http://127.0.0.1:8000/cancel/",
    )

    print(f"Session ID: {session.id}")  # Log the session ID for verification
    return JsonResponse({'sessionId': session.id})


def success(request):
    return render(request, 'travel/success.html')

from django.shortcuts import render, redirect
from .models import Question, Response, Itinerary
from .utils import generate_itinerary  # Your utility function for Hugging Face API

def display_questions(request):
    questions = list(Question.objects.filter(is_active=True).order_by('order'))
    total_questions = len(questions)

    # Initialize index
    if 'current_question_index' not in request.session:
        request.session['current_question_index'] = 0

    current_index = request.session['current_question_index']

    # Check if questionnaire is completed
    if current_index >= total_questions:
        request.session.pop('current_question_index', None)

        # Collect all responses
        responses = Response.objects.filter(session_key=request.session.session_key or 'anonymous')

        # Prepare prompt for LLM
        prompt = ""
        for response in responses:
            prompt += f"{response.question.text}: {response.answer}\n"

        # Send the prompt to the LLM API
        itinerary_text = generate_itinerary(prompt)

        # Show the generated itinerary
        return render(request, 'travel/itinerary_result.html', {
            'itinerary_text': itinerary_text
        })

    current_question = questions[current_index]

    if request.method == 'POST':
        response_value = request.POST.get('answer')
        if response_value:
            # Save response
            Response.objects.create(
                question=current_question,
                answer=response_value,
                session_key=request.session.session_key or 'anonymous'
            )
            # Go to next question
            request.session['current_question_index'] = current_index + 1
            return redirect('display_questions')

    return render(request, 'travel/questions.html', {'question': current_question})

def itinerary_approval(request, itinerary_text):
    if request.method == 'POST':
        if 'approve' in request.POST:
            # Save the itinerary in the database
            itinerary = Itinerary.objects.create(
                user=request.user,
                content=itinerary_text,
                approved=True
            )
            return redirect('profile')  # Redirect to the user's profile

    return render(request, 'travel/itinerary_approval.html', {
        'itinerary_text': itinerary_text
    })
