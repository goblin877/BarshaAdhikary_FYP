from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import booking_view, get_city_suggestions
from travel.views import delete_trip
from travel.views import fetch_hotels

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),  
    path('plan/', views.plan_trip, name='plan_trip'),
    path('about/', views.about, name='about'),
    path('guide/', views.guide_view, name='guide'),
    path('contact/', views.contact, name='contact'),
    path('trip/<int:trip_id>/', views.trip_details, name='trip_details'),
    path('trip/<int:id>/delete/', delete_trip, name='delete_trip'),
    path('booking/', views.booking_view, name='booking'),
    path('itinerary/', views.itinerary, name='itinerary'),
    path('get-cities/', get_city_suggestions, name='get_city_suggestions'),
    path('hotel-search/', views.get_hotels, name='hotel_search'), 
    path('search-flights/', views.search_flights_page, name='search_flights_page'),
    path('flight-booking/', views.flight_booking, name='flight_booking'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/process/', views.payment_process, name='payment_process'),
    path('fetch_hotels/', fetch_hotels, name='fetch_hotels'),
    path('book_hotel/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('questions/', views.display_questions, name='display_questions'),
    path('generate-itinerary/', views.generate_itinerary, name='generate_itinerary'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
