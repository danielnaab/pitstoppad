from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^test/$', direct_to_template, {'template': 'gadget/base_gadget.html'}, name='test_gadget'),
)
