from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from models import *

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule

class ScheduleItemForm(ModelForm):
    class Meta:
        model = ScheduleItem

class ScheduleItemActionForm(ModelForm):
    class Meta:
        model = ScheduleItemAction
