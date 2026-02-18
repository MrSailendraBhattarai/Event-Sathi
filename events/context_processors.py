from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        notes = Notification.objects.filter(user=request.user)
        return {
            'notifications': notes,
            'unread_notifications_count': notes.filter(is_read=False).count()
        }
    return {}