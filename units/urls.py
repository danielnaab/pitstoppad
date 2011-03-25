from django.conf.urls.defaults import *

from units.views import *

urlpatterns = patterns('',
    url(r'^set_units/$', 'units.views.set_units', name="set_units"),
)
