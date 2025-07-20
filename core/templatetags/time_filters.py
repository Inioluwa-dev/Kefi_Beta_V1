from django import template
from django.utils import timezone
from datetime import datetime
import pytz

register = template.Library()

@register.filter
def nigeria_time(value):
    """Convert UTC time to Nigeria time (WAT)"""
    if value:
        # Convert to Nigeria timezone
        nigeria_tz = pytz.timezone('Africa/Lagos')
        if timezone.is_aware(value):
            return value.astimezone(nigeria_tz)
        else:
            # If naive datetime, assume it's UTC
            utc_tz = pytz.UTC
            utc_time = utc_tz.localize(value)
            return utc_time.astimezone(nigeria_tz)
    return value

@register.filter
def smart_time(value):
    """Display time in a smart format with timezone info"""
    if value:
        nigeria_time = nigeria_time(value)
        now = timezone.now()
        diff = now - value
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "Just now"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        else:
            return nigeria_time.strftime('%b %d, %H:%M')
    return value 