from django import forms

from units.middleware import *
from utils.forms import MyDateField

from models import *

class GarageVehicleForm(forms.ModelForm):
    
    purchase_date = MyDateField()
    
    def __init__(self, *args, **kwargs):
        super(GarageVehicleForm, self).__init__(*args, **kwargs)
        self.fields['notes'].widget.attrs['rows'] = 2
        self.fields['vehicle'].widget = forms.HiddenInput()
    
    def save(self, *args, **kwargs):
        super(GarageVehicleForm, self).save(*args, **kwargs)
    
    class Meta:
        model = GarageVehicle
        exclude = ('log', 'garage')
