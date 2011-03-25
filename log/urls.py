from django.conf.urls.defaults import *

from log.models import *
from log.views import *

urlpatterns = patterns('',
    # all blog posts
    #url(r'^$', 'log.views.logs', name="logs"),
    url(r'^browse/$', 'log.views.logs', name="log_browse"),
    url(r'^users/(?P<username>[\w]+)/$', 'log.views.logs', name="log_user_list"),
    url(r'^users/(?P<username>[\w]+)/(?P<log_id>[0-9])/$', 'log.views.view_log', name="log_view"),
    url(r'^users/(?P<username>[\w]+)/(?P<log_id>[0-9])/actions/(?P<action_id>[0-9]+)/$', 'log.views.log_action_view', name="log_action_view"),

    url(r'^new/$', 'log.views.edit', name='log_add_new'),
    
    url(r'^edit/(?P<log_id>[0-9]+)/$', 'log.views.edit', name='log_edit'),
    url(r'^edit/(?P<log_id>[0-9]+)/action/new/$', 'log.views.edit_action', name='new_action'),
    url(r'^edit/(?P<log_id>[0-9]+)/action/(?P<action_id>[0-9]+)/$', 'log.views.edit_action', name='edit_action'),
)
