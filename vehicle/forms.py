from django import forms

from models import *

def DynamicVehicleSelectForm(*args, **kwargs):
    """
    Returns a form for selecting an EPAVehicle, pre-populated with the subset of vehicles
    matching args[0]['year'] and args[0]['make']
    """
    
    values = {}
    if len(args) > 0:
        values = args[0]
    
    year = int(values.get('year', 0))
    make = values.get('make', None)
    if make == '': make = None
    model = values.get('model', None)
    if model == '': model = None
    
    valid_years = EPA_VEHICLE_YEARS
    valid_makes = ()
    if year != 0:
        values = EPAVehicle.objects.filter(year=int(year)).distinct_makes()
        valid_makes = [(None, '')] + [(value['manufacturer'], value['manufacturer']) for value in values]
    valid_models = ()
    if make:
        values = EPAVehicle.objects.filter(year=year, manufacturer=make).distinct_models()
        valid_models = [(None, '')] + [(value['model'], value['model']) for value in values]
    
    class VehicleSelectForm(forms.Form):
        year = forms.ChoiceField(widget=forms.Select(attrs={
                'width': '6em', 'style': 'width: 6em;'}),
            choices=valid_years, required=True)
        make = forms.ChoiceField(widget=forms.Select(attrs={'width': '10em', 'style': 'width: 10em'}),
            choices=valid_makes, required=True)
        model = forms.ChoiceField(widget=forms.Select(attrs={
            'width': '10em', 'style': 'width: 10em;'}),
            choices=valid_models, required=True)
        
        def is_valid(self, *args, **kwargs):
            super(VehicleSelectForm, self).is_valid(*args, **kwargs)
            
            # Always return false.  This form is just used for getting a "vehicle add" url,
            # and is never "completed".
            return False

        def __init__(self, *args, **kwargs):
            super(VehicleSelectForm, self).__init__(*args, **kwargs)
            
            year_attrs = self.fields['year'].widget.attrs
            make_attrs = self.fields['make'].widget.attrs
            model_attrs = self.fields['model'].widget.attrs
            
            year_attrs['onchange'] = 'this.form.make.disabled=true; this.form.model.disabled=true; $(this.form).ajaxSubmit(ajax_submit_handlers);'
            make_attrs['onchange'] = 'this.form.model.disabled=true; $(this.form).ajaxSubmit(ajax_submit_handlers);'
            model_attrs['onchange'] = '$(this.form).ajaxSubmit(ajax_submit_handlers);'
            
            if len(valid_makes) is 0:
                make_attrs['disabled'] = True
            if len(valid_models) is 0:
                model_attrs['disabled'] = True
        
        def get_matching_vehicles(self):
            if super(VehicleSelectForm, self).is_valid():
                vals = self.cleaned_data
                return EPAVehicle.objects.filter(year=vals['year'], manufacturer=vals['make'], model=vals['model'])
            else:
                return None

    return VehicleSelectForm(*args, **kwargs)
