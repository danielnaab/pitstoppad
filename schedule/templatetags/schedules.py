from django import template

from schedule.forms import *
from schedule.models import *

register = template.Library()

@register.inclusion_tag('include/schedule/templatetags/item_form.html')
def schedule_item_form(schedule_item):
    form = ScheduleItemForm(instance=schedule_item)
    return {'form': form, 'schedule_item': schedule_item}

@register.inclusion_tag('include/schedule/templatetags/item_action_form.html')
def schedule_item_action_form(schedule_item_action):
    form = ScheduleItemActionForm(instance=schedule_item_action)
    return {'form': form, 'schedule_item_action': schedule_item_action}
