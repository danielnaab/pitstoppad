# Django AJAX form validation view
#
# Usage: see http://eikke.com/?p=17
#
# Copyright (c) 2007 Nicolas Trangez (eikke@eikke.com)
# 
# This code is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
# See the GNU General Public License for more details.
#

from django.views.decorators.http import require_POST
from django.utils import simplejson
import django.newforms as forms
from django.http import HttpResponse

@require_POST
def validate_form(request, form_class=None, format='json', args=None, kwargs=None):
    kwargs = kwargs or {}
    args = args or []

    post = request.POST.copy()

    if not form_class:
        if not 'form_class' in post.keys():
            raise Exception, 'form_class not set'
        form_class = post['form_class']
        del post['form_class']

    if isinstance(form_class, forms.BaseForm):
        form_class = form_class.__class__
    elif isinstance(form_class, basestring):
        module_name, class_name = '.'.join(form_class.split('.')[:-1]), form_class.split('.')[-1]
        module = __import__(module_name, globals(), None, class_name)
        form_class = module.__dict__[class_name]
    elif issubclass(form_class, forms.BaseForm):
        form_class = form_class
    else:
        raise Exception, 'Only django.newforms.Form, class inheriting from django.newforms.BaseForm or basestring types are accepted as form_class argument'

    form = form_class(data=post, *args, **kwargs)

    serializers = {
        'json': (simplejson.dumps, 'application/json', )
    }
    serializer = serializers.get(format, None)
    if not serializer:
        raise Exception, 'No serializer found for format %s' % format


    if form.is_valid():
        reply = {'form_valid': True, 'form_num_errors': 0, }
    else:
        reply = {'form_valid': False, 'form_num_errors': len(form.errors), }
        reply['errors'] = dict()
        for field in form.errors:
            reply['errors'][field] = [unicode(error) for error in form.errors[field]]

    serialized = serializer[0](reply)
    return HttpResponse(serialized, mimetype=serializer[1])
