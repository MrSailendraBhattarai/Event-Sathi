from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .forms import EventForm
from .models import Event, Category

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.is_approved = False 
            event.save()
            messages.success(request, "Success! Your event has been submitted for approval.")
            return redirect('create_event') 
        else:
            messages.error(request, "There was an error in your form. Please check the details.")
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

def home(request):
    # Only show upcoming approved events on home
    events = Event.objects.filter(is_approved=True, start_date__gte=timezone.now()).order_by('start_date')
    query = request.GET.get('q')
    if query:
        events = events.filter(title__icontains=query)
    return render(request, 'events/home.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

def explore_events(request):
    events = Event.objects.filter(is_approved=True)
    categories = Category.objects.all()
    now = timezone.now()

    # 1. Search Filter
    search_query = request.GET.get('search')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    # 2. Category Filter
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)

    # 3. Date Filter
    date_filter = request.GET.get('date_filter')
    if date_filter == 'today':
        events = events.filter(start_date__date=now.date())
    elif date_filter == 'tomorrow':
        events = events.filter(start_date__date=now.date() + timedelta(days=1))
    elif date_filter == 'this_week':
        week_end = now.date() + timedelta(days=7)
        events = events.filter(start_date__date__range=[now.date(), week_end])
    elif date_filter == 'weekend':
        events = events.filter(start_date__week_day__in=[7, 1])

    # 4. Price Range Filter (NEW)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        events = events.filter(ticket_price__gte=min_price)
    if max_price:
        events = events.filter(ticket_price__lte=max_price)

    # 5. Sorting
    sort = request.GET.get('sort')
    if sort == 'newest':
        events = events.order_by('-created_at')
    else:
        events = events.order_by('start_date')

    context = {
        'events': events,
        'categories': categories,
        'current_date_filter': date_filter,
    }
    return render(request, 'events/explore.html', context)

def payment_options(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/payment_options.html', {'event': event})

def process_payment(request, event_id):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        event = get_object_or_404(Event, id=event_id)
        messages.success(request, f"Redirecting to {payment_method} for {event.title}...")
        return render(request, 'events/payment_processing.html', {
            'method': payment_method,
            'event': event
        })
    return redirect('payment_options', event_id=event_id)

from django.contrib.auth import login
from .forms import SignUpForm # You would create this form

def register(request):
    role = request.GET.get('role', 'user') # Get role from URL: ?role=organizer
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create the profile with the selected role
            UserProfile.objects.create(user=user, role=request.POST.get('role'))
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/register.html', {'form': form, 'role': role})
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import UserProfile

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            
            # This creates the Profile linked to your Custom User
            UserProfile.objects.create(user=user, role=role)
            
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Event

@login_required
def organizer_dashboard(request):
    # Security check
    if request.user.userprofile.role != 'organizer':
        return redirect('home')

    # Fetch events owned by this user
    my_events = Event.objects.filter(organizer=request.user)
    
    # Calculate stats
    stats = {
        'total': my_events.count(),
        'approved': my_events.filter(is_approved=True).count(),
        'pending': my_events.filter(is_approved=False).count(),
    }

    return render(request, 'events/organizer_dashboard.html', {
        'events': my_events,
        'stats': stats
    })

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def login_redirect(request):
    """
    Determines where to send the user after a successful login 
    based on their profile role.
    """
    try:
        if request.user.userprofile.role == 'organizer':
            return redirect('organizer_dashboard')
    except AttributeError:
        # Fallback if for some reason the user doesn't have a profile
        pass
        
    return redirect('home')

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

def organizer_public_profile(request, username):
    # Fetch the user by username
    organizer = get_object_or_404(User, username=username)
    
    # Ensure they are actually an organizer
    if organizer.userprofile.role != 'organizer':
        return redirect('home')
        
    # Get only their approved events
    events = Event.objects.filter(organizer=organizer, is_approved=True)
    
    return render(request, 'events/organizer_profile.html', {
        'organizer': organizer,
        'events': events
    })

from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import EventForm # Assuming you have an EventForm

@login_required
def edit_event(request, event_id):
    # Fetch the event or 404
    event = get_object_or_404(Event, id=event_id)
    
    # Security: Ensure only the owner can edit
    if event.organizer != request.user:
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('home')

    if request.method == 'POST':
        # instance=event tells Django to update the existing record
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{event.title}' has been updated successfully!")
            return redirect('organizer_dashboard')
    else:
        # Pre-fill the form with existing data
        form = EventForm(instance=event)
    
    return render(request, 'events/edit_event.html', {
        'form': form,
        'event': event
    })
@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Security check: only the owner can delete
    if event.organizer != request.user:
        messages.error(request, "You don't have permission to delete this.")
        return redirect('organizer_dashboard')
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('organizer_dashboard')
        
    return redirect('organizer_dashboard')

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Event, Interest

@login_required
def user_profile(request):
    # Get all events the user has marked as "Interested"
    interested_events = Event.objects.filter(interested_users__user=request.user)
    return render(request, 'events/user_profile.html', {
        'interested_events': interested_events
    })

@login_required
def toggle_interest(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        interest, created = Interest.objects.get_or_create(user=request.user, event=event)
        
        if not created:
            interest.delete()
            is_interested = False
        else:
            is_interested = True
            
        return JsonResponse({
            'is_interested': is_interested,
            'count': event.interested_users.count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)