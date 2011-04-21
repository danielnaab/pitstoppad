from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail

from html_helpers.ajax import FormHandler, handles_forms
from vehicle.forms import DynamicVehicleSelectForm

from forms import *
from models import *

@login_required
def browse(request, username=None, template_name='garage/browse.html'):
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

def garage_form_handler(request, username):
    if username == None:
        garage = request.user.garage
    else:
        try:
            garage = Garage.objects.get(user__username=username)
        except:
            raise Http404()
    
    form_handler = FormHandler()
    
    garage_vehicles = garage.garagevehicle_set.all()
    for garage_vehicle in garage_vehicles:
        form = GarageVehicleForm(instance=garage_vehicle, prefix=garage_vehicle.id)
        form_handler.add_form(GarageVehicleForm, garage_vehicle.id, params={'form': form, 'instance': garage_vehicle, 'prefix': garage_vehicle.id, 'template': 'garage/include/form_garagevehicle.html'})
    
    show_what_next = False
    new_vehicle_id = -1
    if request.GET:
        new_vehicle_id = int(request.GET.get('add_vehicle', -1))
        try:
            show_what_next = request.GET['what_next']
            show_what_next = True
        except:
            pass
    
    new_garage_vehicle = None
    add_new_in_progress = False
    if new_vehicle_id is not -1:
        try:
            new_vehicle = EPAVehicle.objects.get(id=new_vehicle_id)
            new_garage_vehicle = GarageVehicle(vehicle=new_vehicle, garage=garage)
            add_new_in_progress = True
        except:
            raise Http404()
    else:
        new_garage_vehicle = GarageVehicle(garage=garage)
        
        form = DynamicVehicleSelectForm(request.POST)
        form_handler.add_form(DynamicVehicleSelectForm, 'select_vehicle', params={
                'form': form, 'prefix': 'select_vehicle', 'submit_text': 'Search Vehicles',
                'init_handler': form_handler.pass_init_handler,
                'submit_classes': 'js_disabled_only',
                'template': 'vehicle/include/vehicle_select_form.html'}
        )
    
    form = GarageVehicleForm(instance=new_garage_vehicle, prefix='new_form')
    form_handler.add_form(GarageVehicleForm, 'new_form', params={
                'form': form,
                'instance': new_garage_vehicle,
                'prefix': 'new_form',
                'submit_text': 'Add To Garage',
                'template': 'garage/include/form_garagevehicle.html'}
    )
    
    return { 'form_handler': form_handler, 'extra_context': {
                    'garage': garage,
                    'add_new_in_progress': add_new_in_progress,
                    'show_edit_ui': True,
                    'show_what_next': show_what_next,
                }
    }


    return view_garage(request, request.user.username)

@login_required
@handles_forms('garage/my_garage.html')
def my_garage(request, username=None):
    return garage_form_handler(request, username)

@login_required
def view_garage(request, username, template_name='garage/my_garage.html'):
    # we re-use the FormHandler from my_garage, so we can use the same template for
    # both "edit" and "view" garage pages.  Since we aren't decorated with @handles_forms,
    # the user won't be able to POST to this url.
    form_handler_dict = garage_form_handler(request, username)
    context = form_handler_dict['extra_context']
    context['form_handler'] = form_handler_dict['form_handler']
    context['show_edit_ui'] = False
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def toggle_follow(request):
    print 1
    if request.POST:
        print 2
        username = request.POST.get('toggle_follow', None)
        if username is None:
            raise Http404()
        
        print 3
        try:
            print 4
            garage = Garage.objects.get(user__username=username)
            print 5
            print 6
        except Garage.DoesNotExist:
            raise Http404()
        
        Following.objects.toggle_follow(request.user.garage, garage)
        print 7
        redirect_path = request.POST.get('redirect_path', '/')
        print redirect_path
        return HttpResponseRedirect(redirect_path)
    
    raise Http404()
