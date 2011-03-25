from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models import get_app
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail

from forms import *
from models import *

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None

def view_schedule(request, schedule_id, template_name='schedule/view.html'):
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except:
        if request.user.is_authenticated():
            request.user.message_set.create(message='The requested schedule was not found.')
        return HttpResponseRedirect(reverse(list_schedules))
    
    can_edit = False
    if schedule.created_by == request.user:
        can_edit = True
    
    return render_to_response(template_name, {
        'schedule': schedule,
        'can_edit': can_edit,
    }, context_instance=RequestContext(request))

def list_schedules(request, username=None, template_name='schedule/schedule_list.html'):
    """
    A basic view that wraps ``django.views.list_detail.object_list``
    """
    if username:
        queryset = Schedule.objects.for_user(username='dan')
    else:
        queryset = Schedule.objects.all()
    return list_detail.object_list(request, **{
        "queryset": queryset,
        "allow_empty": True,
    })

def edit_item(request, schedule_id, item_id):
    schedule_item = ScheduleItem.objects.get(id=item_id)
    schedule = Schedule.objects.get(id=schedule_id)
    if request.method == 'POST':
        # make sure this user has permission to edit this item
        if request.user.id == schedule_item.schedule.created_by.id:
            if schedule_item.schedule.id == schedule.id:
                form = ScheduleItemForm(request.POST, instance=schedule_item)
                if form.is_valid():
                    form.save()
                    
                    redirect_url = reverse('edit_schedule', args=[schedule_id])
                    return HttpResponseRedirect(redirect_url)
    raise Http404()

def edit_action(request, schedule_id, item_id, action_id):
    schedule_item_action = ScheduleItemAction.objects.get(id=action_id)
    schedule_item = ScheduleItem.objects.get(id=item_id)
    schedule = Schedule.objects.get(id=schedule_id)
    if request.method == 'POST':
        # make sure this user has permission to edit this item and that the url isn't mangled (would indicate funny business)
        if request.user.id == schedule_item_action.schedule_item.schedule.created_by.id:
            if schedule_item_action.schedule_item.id == schedule_item.id:
                if schedule_item.schedule.id == schedule.id:
                    form = ScheduleItemActionForm(request.POST, instance=schedule_item_action)
                    if form.is_valid():
                        form.save()
                        
                        redirect_url = reverse('edit_schedule', args=[schedule_id])
                        return HttpResponseRedirect(redirect_url)
    raise Http404()

def edit(request, schedule_id=None, template_name='schedule/edit.html', success_url=None):
    schedule = None
    if schedule_id is not None:
        schedule = Schedule.objects.get(id=schedule_id)
    
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            #form.save(created_by=request.user)
            schedule = form.save()
            if success_url is None:
                success_url = reverse('edit_schedule', args=[schedule_id])
            return HttpResponseRedirect(success_url)
    else:
        form = ScheduleForm(instance=schedule)
    return render_to_response(template_name, {
        'schedule': schedule,
        'form': form,
    }, context_instance=RequestContext(request))
