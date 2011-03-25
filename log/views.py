from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail

from forms import *
from html_helpers.ajax import ajax_form_response, FormHandler, handles_forms
from models import *
from units.middleware import current_fuel_economy_units

def logs(request, username=None, template_name='log/logs.html'):
    """
    A basic view that wraps ``django.views.list_detail.object_list``
    """
    if username:
        queryset = MaintenanceLog.objects.for_user(username=username)
    else:
        queryset = MaintenanceLog.objects.all()
    return list_detail.object_list(request, **{
        "queryset": queryset,
        "allow_empty": True,
        "extra_context": { 'username': username, }
    })

def view_log(request, username, log_id, template_name='log/view.html'):
    try:
        log = MaintenanceLog.objects.get(id=log_id, user__username=username)
    except MaintenanceLog.DoesNotExist:
        raise Http404()
    
    return render_to_response(template_name, {
        'log': log,
        'can_edit': request.user and request.user == log.user,
    }, context_instance=RequestContext(request))

def log_action_view(request, username, log_id, action_id, template_name='log/action_view.html'):
    try:
        action = MaintenanceAction.objects.get(id=action_id, log__id=log_id, log__user__username=username)
    except MaintenanceAction.DoesNotExist:
        raise Http404()
    
    return render_to_response(template_name, {
        'username': username,
        'log': action.log,
        'action': action,
        'expenses': action.maintenanceexpense_set.all(),
        'can_edit': request.user and request.user == action.log.user
    }, context_instance=RequestContext(request))

@login_required
def edit_action(request, log_id, action_id=None):

    log = MaintenanceLog.objects.get(id=log_id)
    if request.method == 'POST':
        # make sure this user has permission to edit this item and that the url isn't mangled (would indicate funny business)
        if request.user.id == log.user.id:
            if action_id:
                action = MaintenanceAction.objects.get(id=action_id)
                if log.id != action.log.id:
                    raise Http404()
            else:
                type = request.POST['type']
                if type == 'FillupAction':
                    action = FillupAction()
                elif type == 'MaintenanceAction':
                    action = MaintenanceAction()
                else:
                    raise Exception, 'Unknown action type: %s' % type
                action.log = log
            
            if action.__class__ is MaintenanceAction:
                form = MaintenanceActionForm(request.POST, instance=action)
            elif action.__class__ is FillupAction:
                form = FillupActionForm(request.POST, instance=action)
            else:
                raise Exception, 'Unknown action class: %s' % str(action.__class__)
            
            if form.is_valid():
                form.save()

            if request.is_ajax():
                return ajax_form_response(request, form)
            else:
                return HttpResponseRedirect(reverse('log_edit', args=[log_id]))
    
    raise Http404()

"""
@login_required
def edit(request, log_id=None, template_name='log/edit.html'):
    log = None
    if log_id is not None:
        log = MaintenanceLog.objects.get(id=log_id)
        # if the current user doesn't own this log, return a 404
        if request.user.id != log.user.id:
            raise Http404()
    
    if request.method == 'POST':
        form = MaintenanceLogForm(request.POST, instance=log)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log = form.save()
            
            if request.is_ajax():
                return ajax_form_response(request, form)
            else:
                return HttpResponseRedirect(reverse('log_edit', args=[log_id]))
        else:
            if request.is_ajax():
                return ajax_form_response(request, form)
            else:
                return render_to_response(template_name, {
                    'log': log,
                    'form': form,
                }, context_instance=RequestContext(request))
    else:
        form = MaintenanceLogForm(instance=log)
        return render_to_response(template_name, {
            'log': log,
            'form': form,
        }, context_instance=RequestContext(request))
"""

@login_required
@handles_forms('log/edit.html')
def edit(request, log_id):
    
    try:
        log = MaintenanceLog.objects.get(id=log_id)
    except MaintenanceLog.DoesNotExist:
        raise Http404()
    
    # Verify that the current user owns this log
    if request.user.id is not log.user.id:
        raise Http404()
    
    form_handler = FormHandler()
    
    add_action_form = None
    init_handler = form_handler.pass_init_handler
    if request.POST and request.POST['form_class_name'] == 'AddNewActionForm':
        add_action_form = AddNewActionForm(log, request.POST, prefix='new_action')
    else:
        add_action_form = AddNewActionForm(log, prefix='new_action')
    
    form_handler.add_form(AddNewActionForm, 'new_action', params={'form': add_action_form,
        'prefix': 'new_action',
        'submit_text': 'Add',
        'init_handler': init_handler,
        'template': add_action_form.get_template(),
        #'clear_form_on_save': True,
    })
    
    #for action in MaintenanceAction.objects.filter(log=log):
    for action in FillupAction.objects.filter(log=log).order_by('mileage').order_by('date'):
        form = FillupActionForm(instance=action, prefix=action.id)
        form_handler.add_form(FillupActionForm, action.id, params={'form': form,
            'instance': action,
            'prefix': action.id,
            'template': form.get_template(),
        })
    
    action = FillupAction()
    action.log = log
    form = FillupActionForm(instance=action, prefix='new_form')
    form_handler.add_form(FillupActionForm, 'new_form', params={'form': form, 'instance': action,
        'prefix': 'new_form',
        'template': form.get_template(),
        'clear_form_on_save': True,
    })
    
    return { 'form_handler': form_handler, 'extra_context': { 'log': log,
                                                              'fuel_economy_units': current_fuel_economy_units(),
                                                            } }
