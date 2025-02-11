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
import requests
from django.http import JsonResponse
from .models import Trip
from datetime import date
from .models import TripPlan
from django.utils import timezone

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
@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_trips = Trip.objects.filter(user=request.user)  # Fetch user's trips

    return render(request, 'travel/profile.html', {"user_profile": user_profile, "user_trips": user_trips})
@login_required
def edit_profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_profile.bio = request.POST.get("bio")
        if request.FILES.get("profile_picture"):
            user_profile.profile_picture = request.FILES.get("profile_picture")
        user_profile.save()

        return redirect("profile")  # Redirect to profile page after saving

    return render(request, "travel/edit_profile.html", {"user_profile": user_profile})
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
@login_required
def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id, user=request.user)  # Ensure the trip belongs to the logged-in user
    return render(request, 'travel/trip_details.html', {'trip': trip})

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
