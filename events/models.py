from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


# 1. Custom User Model
class User(AbstractUser):
    # This replaces the need for UserProfile if you want!
    # But since you have logic for both, we keep them distinct.
    is_poster = models.BooleanField(default=False)
    is_verified_poster = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# 2. User Profile (Linked to the Custom User)
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User/Attendee'),
        ('organizer', 'Event Organizer'),
    )
    # IMPORTANT: Point to the setting, not the direct 'User' class
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# 3. Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(
        max_length=50, 
        help_text="e.g., bi-music", 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# 4. Event Model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    banner_image = models.ImageField(upload_to='event_banners/', null=True, blank=True)
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def status_display(self):
        now = timezone.now()
        if now < self.start_date:
            return f"Starts {self.start_date.strftime('%b %d, %I:%M %p')}"
        elif self.end_date and now > self.end_date:
            return "Ended"
        return "Live Now"

# Add this to support your "Interested" feature
class Interest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interests')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='interested_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='interested_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event') # Prevents double-clicking