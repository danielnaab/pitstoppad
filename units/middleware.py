from models import *

# threadlocals middleware
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_volume_unit():
    return getattr(_thread_locals, 'volume_unit', 0)
def get_current_distance_unit():
    return getattr(_thread_locals, 'distance_unit', 0)

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            (_thread_locals.volume_unit, _thread_locals.distance_unit) = get_user_units(user)
        else:
            try: _thread_locals.volume_unit = int(request.COOKIES.get('volume_unit', 0))
            except ValueError: _thread_locals.volume_unit = 0   # safety - will catch if the user modified the cookie to a non-int
            try: _thread_locals.distance_unit = int(request.COOKIES.get('distance_unit', 0))
            except ValueError: _thread_locals.distance_unit = 0 # safety - will catch if the user modified the cookie to a non-int
            
        setattr(request, 'volume_unit', _thread_locals.volume_unit)
        setattr(request, 'distance_unit', _thread_locals.distance_unit)
        setattr(request, 'metric', _thread_locals.volume_unit and _thread_locals.distance_unit)

def current_fuel_economy_units():
    pass
    economy_units = ''
    if get_current_distance_unit() == MILES:
        economy_units = 'mp'
    else:
        economy_units = 'kp'
    if get_current_volume_unit() == GALLONS:
        economy_units = economy_units + 'g'
    else:
        economy_units = economy_units + 'l'
    return economy_units

def get_current_distance_unit_label():
    pass
    if get_current_distance_unit() == MILES:
        return 'Miles'
    else:
        return 'Kilometers'

def get_current_volume_unit_label():
    if get_current_volume_unit() == GALLONS:
        return 'Gallons'
    else:
        return 'Liters'
