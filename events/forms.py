from django import forms
from .models import Event, Category
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'start_date', 
            'end_date', 'ticket_price', 'banner_image', 
            'address', 'latitude', 'longitude'
        ]

    class Meta:
        model = Event
        # 1. 'date_time' is removed and replaced with 'start_date' and 'end_date'
        fields = [
            'title', 'description', 'category', 'start_date', 'end_date',
            'ticket_price', 'banner_image', 'address', 'latitude', 'longitude'
        ]
        # 2. Widgets must match the fields listed above
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, City, Landmark'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model # Add this

User = get_user_model() # Get the active model (events.User)

class SignUpForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('user', 'User/Attendee'), ('organizer', 'Event Organizer')],
        initial='user',
        # Adding some basic styling to the role selection
        widget=forms.Select(attrs={'class': 'w-full border-none bg-transparent outline-none'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full border-none bg-transparent outline-none'}))

    class Meta:
        model = User # This now points to your custom User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border-none bg-transparent outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border-none bg-transparent outline-none'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user