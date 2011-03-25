from django import template

import units

register = template.Library()

@register.simple_tag
def current_fuel_economy_units():
    return units.current_fuel_economy_units()

@register.simple_tag
def is_metric():
    return units.get_current_volume_unit() and units.get_current_distance_unit()
