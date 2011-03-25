from django import template

from ..models import Following

register = template.Library()

@register.inclusion_tag('garage/include/toggle_follow_form.html')
def toggle_follow_form(follower, followed, redirect_path):
    return {'is_following': Following.objects.is_following(follower, followed),
        'followed': followed, 'redirect_path': redirect_path}

@register.inclusion_tag('garage/include/garage_short_bio.html')
def garage_short_bio(garage, post_count=5):
    recent_posts = garage.user.added_posts.order_by('created_at')[:post_count]
    return {'garage': garage, 'recent_posts': recent_posts}
