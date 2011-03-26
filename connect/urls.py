from django.conf.urls.defaults import *

urlpatterns = patterns('connect.views',
    url(r'^after/?$', 'after', name='after'),
)
