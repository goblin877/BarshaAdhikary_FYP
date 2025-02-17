from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import booking_view, get_city_suggestions
from travel.views import delete_trip

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),  # Route for editing profile
    path('plan/', views.plan_trip, name='plan_trip'),
    path('about/', views.about, name='about'),
    path('guide/', views.guide_view, name='guide'),
    path('contact/', views.contact, name='contact'),
    path('trip/<int:trip_id>/', views.trip_details, name='trip_details'),
    path('trip/<int:id>/delete/', delete_trip, name='delete_trip'),
    path('booking/', booking_view, name='booking'),
    path('itinerary/', views.itinerary, name='itinerary'),
    path('get-cities/', get_city_suggestions, name='get_city_suggestions'),  # For city suggestions
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
