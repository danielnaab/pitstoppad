import os
import settings

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    url(r'^$', direct_to_template, {'template': 'homepage.html'}, name='home'),
    url(r'^about/$', direct_to_template, {'template': 'about/about.html'}, name='about'),
    url(r'^terms-and-conditions/$', direct_to_template, {'template': 'about/terms.html'}, name='terms'),
    url(r'^privacy-policy/$', direct_to_template, {'template': 'about/privacy.html'}, name='privacy'),
    
    # Vehicle log URLs
    (r'^units/', include('units.urls')),
    (r'^logs/', include('log.urls')),
    (r'^schedules/', include('schedule.urls')),
    (r'^vehicles/', include('vehicle.urls')),
    (r'^garage/', include('garage.urls')),
    (r'^gadgets/', include('gadget.urls')),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    )
