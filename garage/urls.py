from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^browse/$', 'garage.views.browse', name="garage_browse"),
    url(r'^my_garage/$', 'garage.views.my_garage', name="garage_my_garage"),
    url(r'^users/(?P<username>[\w]+)/$', 'garage.views.view_garage', name="garage_view_garage"),

    url(r'^follow/$', 'garage.views.toggle_follow', name="garage_toggle_follow"),
)
