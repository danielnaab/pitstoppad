from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail

from forms import *
from models import *

def parametrize_checkslug(model, slug_mapping, param):
    for mapping in slug_mapping:
        if mapping[0] == param:
            return mapping[1]
    return param

def parametrize(model, slug_mapping, parameters):
    params = None
    user_params = None
    if parameters:
        parameters = parameters.split('/')
        if not len(parameters) % 2:
            params, user_params = dict(), dict()
            for index in range(0, len(parameters), 2):
                user_param = parameters[index]
                param = parametrize_checkslug(model, slug_mapping, user_param)
                model._meta.get_field(param)
                # str() the key, because filter(**params) doesn't like unicode keynames
                params[str(param)] = parameters[index+1]
                user_params[user_param] = parameters[index+1]
    return params, user_params

def vehicles(request, parameters=None):
    """
    """
    queryset = EPAVehicle.objects.all().order_by('model').order_by('manufacturer')
    extra_context = dict( transmissions=TRANSMISSION_OPTIONS,
        transmission_speeds=TRANSMISSION_SPEED_OPTIONS,
        vehicle_classes=VEHICLE_CLASSES,
    )
    
    try:
        parameters, user_parameters = parametrize(EPAVehicle, EPAVEHICLE_FIELD_SLUG_MAPPING, parameters)
    except FieldDoesNotExist:
        raise Http404()
    if parameters:
        queryset = queryset.filter(**parameters)
        extra_context.update(parameters)
        extra_context['parameters'] = parameters
        
        # Set the "proper", human readable version of each parameter in user_parameters
        for key, value in user_parameters.iteritems():
            if not parameters.has_key(key):
                user_parameters[key] = queryset[0].__getattribute__(key)
        extra_context['user_parameters'] = user_parameters
    
    extra_context["results_per_page"] = 10
    
    extra_context['base_queryset'] = queryset
    
    return list_detail.object_list(request, **{
        'template_name': 'vehicle/browse.html',
        'queryset': queryset,
        'allow_empty': True,
        'extra_context': extra_context,
    })

def view(request, vehicle_id, slug=None, template_name='vehicle/view.html'):
    """
    """
    try:
        vehicle = EPAVehicle.objects.get(id=vehicle_id)
    except EPAVehicle.DoesNotExist:
        raise Http404()
    
    return render_to_response(template_name, {
        'vehicle': vehicle,
    }, context_instance=RequestContext(request))


from html_helpers.ajax import handles_forms, FormHandler
@handles_forms(template_name='vehicle/tests/vehicle_select.html')
def vehicle_select_form(request):
    prefix = 'select_vehicle'
    form = DynamicVehicleSelectForm(request.POST)
    
    form_handler = FormHandler()
    form_handler.add_form(DynamicVehicleSelectForm, 'select_vehicle', params={
            'form': form, 'prefix': 'select_vehicle', 'submit_text': 'Search Vehicles',
            'init_handler': form_handler.pass_init_handler,
            'submit_classes': 'js_disabled_only',
            'template': 'vehicle/include/vehicle_select_form.html'}
    )
    
    return { 'form_handler': form_handler, 'extra_context': {} }
