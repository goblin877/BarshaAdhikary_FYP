from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import CustomUserCreationForm, TripForm, ProfileForm
from .models import TravelGuide, UserProfile
from .forms import TripForm, ProfileForm
from .models import Trip
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.shortcuts import render


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
    user_profile = UserProfile.objects.get(user=request.user)
    trips = Trip.objects.filter(user=request.user)
    return render(request, 'travel/profile.html', {'user_profile': user_profile, 'trips': trips})

# Edit Profile view
@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'travel/edit_profile.html', {'form': form})
# Plan Trip view
@login_required
def plan_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user  # Assign the trip to the logged-in user
            trip.save()
            messages.success(request, "Trip planned successfully!")
            return redirect('profile')  # Redirect to profile page after saving the trip
    else:
        form = TripForm()

    return render(request, 'travel/plan_trip.html', {'form': form})


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
@login_required
def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id, user=request.user)
    return render(request, 'travel/trip_details.html', {'trip': trip})

def booking_view(request):
    return render(request, 'travel/booking.html')

def itinerary(request):
    return render(request, 'travel/itinerary.html')
