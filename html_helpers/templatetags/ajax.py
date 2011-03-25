from django import template

register = template.Library()

@register.inclusion_tag('include/html_helpers/formhandler_form.html')
def formhandler_form(form_class_name, form_dict, extra_handler=None):
    return {'form_class_name': form_class_name, 'form_dict': form_dict, 'extra_handler': extra_handler, 'use_ajax': True}

@register.inclusion_tag('include/html_helpers/formhandler_form.html')
def formhandler_form_no_ajax(form_class_name, form_dict, extra_handler=None):
    return {'form_class_name': form_class_name, 'form_dict': form_dict, 'extra_handler': extra_handler, 'use_ajax': False}
