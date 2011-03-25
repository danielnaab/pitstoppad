from django.http import Http404, HttpResponseRedirect

from models import *

def set_units(request):
    if request.POST:
        units = request.POST.get('units', None)
        redirect_path = request.POST.get('redirect_path', '/')
        
        if units and redirect_path:
            units = int(units)
            response = HttpResponseRedirect(redirect_path)
            
            if request.user.is_authenticated():
                set_user_units(request.user, units, units)
            else:
                # if user is not logged in, saved the new units in a cookie instead of UnitsPref:
                response.set_cookie('volume_unit', units)
                response.set_cookie('distance_unit', units)
            
            return response
    
    raise Http404()
