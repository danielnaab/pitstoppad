from django.conf.urls.defaults import *
from django.views.generic import list_detail

from settings import DEBUG

urlpatterns = patterns('',
    url(r'^browse/$', 'vehicle.views.vehicles', name="vehicle_browse"),
    url(r'^browse/(?P<parameters>.+)/+$', 'vehicle.views.vehicles', name="vehicle_browse"),
    
    url(r'^view/(?P<vehicle_id>[0-9]+)/$', 'vehicle.views.view', name="vehicle_view"),
    url(r'^view/(?P<slug>.+)/(?P<vehicle_id>[0-9]+)/$', 'vehicle.views.view', name="vehicle_view"),
)

if DEBUG:
    urlpatterns += patterns('',
        url(r'^select_form/$', 'vehicle.views.vehicle_select_form', name="vehicle_select_form"),
    )
