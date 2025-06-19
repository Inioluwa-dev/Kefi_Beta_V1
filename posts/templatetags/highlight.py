import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

HASHTAG_PATTERN = re.compile(r'#(\w+)')
MENTION_PATTERN = re.compile(r'@(\w+)')

def link_hashtags(text):
    return HASHTAG_PATTERN.sub(r'<a href="/posts/feed/?tag=\1" class="text-primary">#\1</a>', text)

def link_mentions(text):
    return MENTION_PATTERN.sub(r'<a href="/users/profile/\1/" class="text-info">@\1</a>', text)

@register.filter
def highlight_tags_mentions(value):
    value = link_hashtags(value)
    value = link_mentions(value)
    return mark_safe(value)
