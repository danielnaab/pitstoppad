from django import template

from ..forms import *

register = template.Library()

@register.inclusion_tag('log/include/templatetags/action_form_head.html')
def action_form_head(log):
    actions = None
    if log:
        actions = log.maintenanceaction_set.all()
    return {'actions': actions}

@register.inclusion_tag('log/include/templatetags/new_action_form.html')
def new_action_form():
    return {'fillup_form': FillupActionForm(), 'action_form': MaintenanceActionForm()}

@register.inclusion_tag('log/include/templatetags/action_form.html')
def maintenance_action_form(action=None):
    form = None
    caption = None
    if action.__class__ is MaintenanceAction:
        form = MaintenanceActionForm(instance=action)
        caption = 'Maintenance Action'
    elif action.__class__ is FillupAction:
        form = FillupActionForm(instance=action)
        caption = 'Fuel fillup'
    else:
        raise Exception, 'Unknown maintenance action class: %s' % str(action.__class__)
    
    action_form_id = 'action_form_%s' % action.id
    
    return {'form': form, 'action': action, 'caption': caption, 'action_form_id': action_form_id}
