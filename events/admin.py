from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# This allows you to see the custom fields in the Admin panel
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Poster Status', {'fields': ('is_poster', 'is_verified_poster')}),
    )

admin.site.register(User, CustomUserAdmin)

from .models import Category, Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'is_approved', 'start_date', 'created_at')
    list_editable = ('is_approved',) 
    list_filter = ('is_approved', 'category')
    # Add this line to activate your custom action
    actions = ['approve_events']

    def approve_events(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} events were successfully approved.")
    
    approve_events.short_description = "✅ Approve selected events"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')