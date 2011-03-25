from django import template
from django.db.models.fields import IntegerField

from ..models import *

register = template.Library()

@register.simple_tag
def epavehicle_field_display_name(field_name, field_value):
    vehicle = EPAVehicle()
    
    try:
        vehicle.__setattr__(field_name, int(field_value))
        return vehicle.__getattribute__('get_%s_display' % field_name)()
    except: pass
    
    return field_value

@register.inclusion_tag('vehicle/include/vehicle_images.html')
def vehicle_image_search(search_terms):
    return {'search_terms': search_terms}

@register.simple_tag
def display_for_choices_id(choices_tuple, id):
    for choice in choices_tuple:
        if choice[0] == int(id):
            return choice[1]
    raise Exception, 'No matching choice in tuple `%s` for id `%s`' % (choices_tuple, id)
