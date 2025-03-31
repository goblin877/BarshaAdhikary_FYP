from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trip, UserProfile
from .models import Question
from .models import Review
# Custom user creation form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['destination', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500', 'rows': 4}))

# Profile form to handle user profile updates, including image upload
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'dob', 'contact_number', 'profile_picture', 'bio']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    # Optionally, you can add custom validation or processing here for the image upload
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # You can add any validation for the image file (e.g., file size, format, etc.)
            pass
        return profile_picture
    
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'options']  # Include the fields you want to display (e.g., text and options)

    # This function will help you render the options as choices for multiple-choice questions
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if self.instance.question_type in ['age_group', 'travel_companion', 'food_preference', 'activity_type', 'place_type']:
            self.fields['options'].widget = forms.Select(choices=[(option, option) for option in self.instance.options])  


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'review_text', 'rating', 'image']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)])
        }             