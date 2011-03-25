from django import forms
from django.contrib.admin import widgets
from django.template.loader import render_to_string

from units.middleware import *
from utils.forms import MyDateField

from models import *

def form_class_for_model(model):
    return {
        MaintenanceAction: MaintenanceActionForm,
        FillupAction: FillupActionForm,
    }[model]

class NewActionStartForm(forms.Form):
    step = forms.IntegerField(initial=-1, widget=forms.HiddenInput)
    
    date = MyDateField(label='Date')
    action_type = forms.ChoiceField(choices=ACTION_TYPE_STRINGS, widget=forms.RadioSelect)
    
    def __init__(self, *args, **kwargs):
        self.extra_return_data = kwargs.pop('extra_return_data', {})
        # stringify all the values in extra_return_data
        if self.extra_return_data:
            for key, value in self.extra_return_data.iteritems():
                self.extra_return_data[key] = str(value)
        
        super(NewActionStartForm, self).__init__(*args, **kwargs)
    
    def get_template(self):
        return None #'log/form_fillupaction.html'
    
    def get_action_form(self, log, date, *args, **kwargs):
        if not self.is_valid():
            raise forms.utils.ValidationError, 'Cannot get_action_form() on invalid form.'
        
        type = int(self.cleaned_data['action_type'])
        model = ACTION_TYPE_MODELS[type][1]
        instance = model(log=log, date=date)
        form_class = form_class_for_model(model)
        return form_class(instance=instance, *args, **kwargs)
    
    def save(self):
        super(NewActionStartForm, self).save()

class FillupActionForm(forms.ModelForm):
    step = forms.IntegerField(initial=id_for(ACTION_TYPE_MODELS, FillupAction), widget=forms.HiddenInput)

    tank_distance = forms.DecimalField(decimal_places=8, max_digits=16)
    fillup_volume = forms.DecimalField(decimal_places=8, max_digits=16)
    mileage_quantity = forms.DecimalField(decimal_places=8, max_digits=16)
    
    def get_template(self):
        return 'log/form_fillupaction.html'
    
    def __init__(self, *args, **kwargs):
        super(FillupActionForm, self).__init__(*args, **kwargs)
        
        date = self.fields['date']
        volume = self.fields['fillup_volume']
        distance = self.fields['tank_distance']
        mileage = self.fields['mileage_quantity']
        
        date.widget = forms.HiddenInput()
        #date.widget.attrs['size'] = '10em'
        volume.widget.attrs['size'] = '4em'
        distance.widget.attrs['size'] = '4em'
        mileage.widget.attrs['size'] = '7em'
        
        distance.label = get_current_distance_unit_label()
        volume.label = get_current_volume_unit_label()
        if self.instance:
            if get_current_distance_unit() == MILES:
                distance.initial = self.instance.miles
                distance.label = 'Tank Miles'
                mileage.initial = self.instance.mileage
                mileage.label = 'Mileage'
            else:
                distance.initial = self.instance.kilometers
                distance.label = 'Tank Kilometers'
                mileage.initial = self.instance.mileage_km
                mileage.label = 'Mileage (km)'
            if get_current_volume_unit() == GALLONS:
                volume.initial = self.instance.gallons
            else:
                volume.initial = self.instance.liters
    
    def save(self, *args, **kwargs):
        if get_current_distance_unit() == MILES:
            self.instance.miles = self.cleaned_data['tank_distance']
            self.instance.mileage = self.cleaned_data['mileage_quantity']
        else:
            self.instance.kilometers = self.cleaned_data['tank_distance']
            self.instance.mileage_km = self.cleaned_data['mileage_quantity']
        if get_current_volume_unit() == GALLONS:
            self.instance.gallons = self.cleaned_data['fillup_volume']
        else:
            self.instance.liters = self.cleaned_data['fillup_volume']
        return super(FillupActionForm, self).save(*args, **kwargs)
        
    def clean_mileage_quantity(self):
        #date = self.cleaned_data['date']
        mileage = self.cleaned_data['mileage_quantity']
        
        (min, max) = MaintenanceAction.objects.valid_mileage_range_for_log_date(self.instance.log, self.instance.date)
        
        if mileage < min:
            raise forms.ValidationError, 'Mileage for this date must no less than %s' % (min)
        elif mileage > max:
            raise forms.ValidationError, 'Mileage for this date must no greater than %s' % (max)
        
        return mileage
    
    class Meta:
        model = FillupAction
        exclude = ('log', 'description', 'liters', 'gallons', 'miles', 'kilometers', 'mileage', 'mileage_km')

class MaintenanceActionForm(forms.ModelForm):
    step = forms.IntegerField(initial=id_for(ACTION_TYPE_MODELS, MaintenanceAction), widget=forms.HiddenInput)
    
    def get_template(self):
        return None #return 'log/form_fillupaction.html'
    
    def __init__(self, *args, **kwargs):
        super(MaintenanceActionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = forms.HiddenInput()
        #self.fields['date'].widget = widgets.AdminDateWidget(attrs={'size': 10})
        #self.fields['mileage'].widget.attrs['size'] = 7
    
    class Meta:
        model = MaintenanceAction
        exclude = ('log')

class MaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        exclude = ('user')
    
    def as_styled(self):
        "Returns this form rendered in divs with CSS classes."
        return self._html_output(u'<div>%(errors)s%(label)s %(field)s%(help_text)s</li>', u'<li>%s</li>', '</li>', u' %s', False)

def AddNewActionForm(log, *args, **kwargs):
    
    values = None
    if len(args) > 0:
        values = args[0]
    
    prefix = kwargs.get('prefix', None)
    if prefix:
        step_field = '%s-step' % (prefix)
        date_field = '%s-date' % (prefix)
    else:
        step_field = 'step'
        date_field = 'date' % (prefix)
    
    # If we're not handling POST data, start at the NewActionStartForm
    if not values:
        return NewActionStartForm(*args, **kwargs)
    else:
        step = values.get(step_field, None)
        if not step:
            raise Exception, 'AddNewActionForm requires the step parameter'
        step = int(step)
        
        if step == -1:
            form = NewActionStartForm(*args, **kwargs)
            
            # If the post failed, re-return the NewActionStartForm
            if not form.is_valid():
                return form
            # Otherwise, return the form for the action type to add.
            else:
                # Remove the data from args so we return an unbound form.
                args = [ arg for arg in args ]
                args.pop(0)
                
                date = form.cleaned_data['date']
                
                return form.get_action_form(log, date, *args, **kwargs)
        else:
            model = ACTION_TYPE_MODELS[step][1]
            if not step:
                raise Exception, 'The date field is required to add a new action.'
            date = values[date_field]
            instance = model(log=log, date=date)
            form = form_class_for_model(model)
            new_form = form(instance=instance, *args, **kwargs)
            
            if not new_form.is_valid():
                return new_form
            else:
                # If the posted form is valid, save it to the database and
                # return the new form again.
                new_form.save()

                # Remove the data from args so we return an unbound form.
                args = [ arg for arg in args ]
                args.pop(0)
                cleaned_data = getattr(new_form, 'cleaned_data', None)
                kwargs['extra_return_data'] = cleaned_data
                
                template = new_form.get_template()
                if template is None: template = 'include/html_helpers/formhandler_inner.html'
                kwargs['extra_return_data']['new_form'] = render_to_string(template,
                    {'form_class_name': new_form.__class__.__name__, 'form': new_form})
                
                return NewActionStartForm(*args, **kwargs)
