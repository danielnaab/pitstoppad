from django import forms
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from log.forms import *

class handles_forms(object):
    def __init__(self, template_name):
        self.template_name = template_name
    
    def __call__(self, func):
        def dec(request, *args, **kwargs):
            view_dict = func(request, *args, **kwargs)
            form_handler = view_dict.get('form_handler', None)
            extra_context = view_dict.get('extra_context', None)
            extra_context['form_handler'] = form_handler
        
            #request = args.get('request', None)
            if request and request.POST:
                form_class_name = request.POST.get('form_class_name', None)
                if not form_class_name: raise Exception('form_class_name is required!')
                form_id = request.POST.get('form_id', None)
                if not form_id: raise Exception('form_id is required!')
                
                form_params = form_handler.params_for_form(form_id=form_id, form_class_name=form_class_name)
                if not form_params: raise Http404()
                
                # instantiate the form with the model instance (if it exists).
                init_handler = form_params.get('init_handler', form_handler.default_modelform_init_handler)
                init_handler(request.POST, form_dict=form_params)
                
                # get the django form class for this form
                form = form_params.get('form', None)
                if not form: raise Http404()
                
                if form.is_valid():
                    form.save()
                    
                    clear_form_on_save = form_params.get('clear_form_on_save', False)
                    if clear_form_on_save:
                        init_handler({}, form_dict=form_params)
                    
                    if request.is_ajax():
                        return ajax_form_response(request, form_params, force_form_as_valid=clear_form_on_save)
                    else:
                        return HttpResponseRedirect(request.path)
                else:
                    if request.is_ajax():
                        return ajax_form_response(request, form_params)
                    else:
                        return render_to_response(self.template_name, extra_context, context_instance=RequestContext(request))
                    
            # If this isn't a valid POST, return the main view
            return render_to_response(self.template_name, extra_context, context_instance=RequestContext(request))
        return dec

class FormHandler:
    def __init__(self):
        """
        forms   Form classes this object is to handle.  Each item is a dictionary of parameters.  See add_form.
        """
        self.forms = {}
    
    def add_form(self, form_class, form_id, params={}):
        form_name = form_class.__name__
        
        params['form_class'] = form_class
        params['form_id'] = str(form_id)
        params.setdefault('submit_text', 'Save')
        
        if not self.forms.has_key(form_name):
            self.forms[form_name] = []
        
        self.forms[form_name].append(params)
        #self.forms[form_name][str(form_id)] = params
    
    def params_for_form(self, form_id, form_class=None, form_class_name=None):
        
        if form_class and form_class_name: raise Exception, 'get_form requires only one of form_class or form_class_name'
        elif not form_class and not form_class_name: raise Exception, 'get_form requires either form_class or form_class_name'
        
        if form_class:
            form_class_name = form_class.__name__
        
        for params in self.forms[form_class_name]:
            if params['form_id'] == str(form_id):
                return params
        
        raise Exception, 'Form with id `%s` not found' % (form_id)
    
    def default_modelform_init_handler(self, data, form_dict):
        form_class = form_dict['form_class']
        form_id = form_dict['form_id']
        prefix = form_dict.get('prefix', None)
        instance = form_dict.get('instance', None)
        form = form_class(data=data, instance=instance, prefix=prefix)
        form_dict['form'] = form

    def pass_init_handler(self, data, form_dict):
        pass
    
    def default_form_init_handler(self, data, form_dict):
        """Initializes form like above, but w/o passing a Model instance."""
        form_class = form_dict['form_class']
        prefix = form_dict.get('prefix', None)
        #form = form_class(data=data, prefix=prefix)
        form = form_class(data=data, prefix=prefix)
        form_dict['form'] = form
    
    """
    def handle_post(self, request, form_class_name, form_id):
        if not request.POST: raise Http404()
        
        _form_class = self.forms.get(form_class_name, None)
        if not _form_class: raise Http404()
        form_params = _form_class[str(form_id)]
        if not form_params: raise Http404()
        
        # Run the init handler for this form.
        # init_handler is responsible for dynamically setting any of the items
        #       in the form's dict, to define how the rest of the handler works.
        #       For instance it may be used to set the form['instance'] value to
        #       the instance the form is editing.
        form_params.get('init_handler', self.default_modelform_init_handler)(request, form_dict=form_params)
        
        # get the django form class for this form
        form = form_params.get('form', None)
        if not form: raise Http404()
        
        # instantiate the form with the model instance (if it exists).
        form(request.POST, instance=form_params.get('instance', None))
    """

def ajax_form_response(request, form_dict, force_form_as_valid=False, format='json'):
    form = form_dict['form']
    
    serializers = {
        'json': (simplejson.dumps, 'application/json', )
    }
    serializer = serializers.get(format, None)
    if not serializer:
        raise Exception, 'No serializer found for format %s' % format
    
    reply = {}
    if not force_form_as_valid:
        if form.is_valid():
            reply['form_valid'] = True
            reply['form_num_errors'] = 0
        else:
            reply['form_valid'] = False
            reply['form_num_errors'] = len(form.errors)
        
        reply['errors'] = dict()
        for field in form.errors:
            reply['errors'][field] = [unicode(error) for error in form.errors[field]]
    else:
        reply['form_valid'] = True
        reply['form_num_errors'] = 0
    
    try:
        reply['extra_return_data'] = form.extra_return_data
    except:
        pass
    
    template = form_dict.get('template', None)
    if template is None:
        template = 'include/html_helpers/formhandler_inner.html'
    reply['new_form'] = render_to_string(template,
        {'form_class_name': form_dict['form_class'].__name__, 'form_dict': form_dict, 'form': form})
    reply['form_class'] = form_dict['form_class'].__name__
    reply['form_id'] = form_dict['form_id']
    
    cleaned_data = getattr(form, 'cleaned_data', None)
    if cleaned_data:
        reply['cleaned_data'] = dict()
        for key, value in cleaned_data.iteritems():
            reply['cleaned_data'][key] = str(value)
    
    serialized = serializer[0](reply)
    return HttpResponse(serialized, mimetype=serializer[1])
