from django.conf.urls.defaults import *
from django.views.generic import list_detail

from schedule.models import *
from schedule.views import *


announcement_detail_info = {
    'queryset': Schedule.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.list_schedules', name='all_schedules'),
    url(r'^view/(?P<schedule_id>[0-9]+)/$', 'schedule.views.view_schedule', name='view_schedule'),
    url(r'^list/(?P<username>[\w]+)/$', 'schedule.views.list_schedules', name='list_schedules'),
    url(r'^new/$', 'schedule.views.edit', name='new_schedule'),
    
    url(r'^edit/(?P<schedule_id>[0-9]+)/$', 'schedule.views.edit', name='edit_schedule'),
    url(r'^edit/(?P<schedule_id>[0-9]+)/item/(?P<item_id>[0-9]+)/$', 'schedule.views.edit_item', name='edit_schedule_item'),
    url(r'^edit/(?P<schedule_id>[0-9]+)/item/(?P<item_id>[0-9]+)/action/(?P<action_id>[0-9]+)/$', 'schedule.views.edit_action', name='edit_schedule_action'),
)
