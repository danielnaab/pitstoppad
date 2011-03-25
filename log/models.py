import decimal
import sys

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from schedule.models import Schedule
from units.middleware import get_current_volume_unit, get_current_distance_unit
from units.models import *
from vehicle.models import EPAVehicle

class MaintenanceLogManager(models.Manager):
    
    def for_user(self, username):
        return self.get_query_set().filter(user__username=username)

class MaintenanceLog(TimeStampedModel):
    
    user = models.ForeignKey(User, verbose_name=_('user'))
    vehicle = models.ForeignKey(EPAVehicle, null=True, blank=True)
    schedule = models.ForeignKey(Schedule, null=True, blank=True)
    
    objects = MaintenanceLogManager()

    def __unicode__(self):
        return '%s (%s)' % (self.vehicle, self.user.username)

class MaintenanceActionManager(models.Manager):
    
    def chronological(self):
        return self.get_query_set().order_by('mileage', 'date')
    
    def valid_mileage_range_for_log_date(self, log, datetime, distance_units=None):
        if distance_units is None:
            distance_units = get_current_distance_unit()
        if distance_units == MILES:
            distance_field = 'mileage'
        else:
            distance_field = 'mileage_km'
        
        base_queryset = self.get_query_set().filter(log=log).values(distance_field)
        try:
            min = base_queryset.filter(date__lt=datetime).order_by('-date')[:1][0][distance_field]
        except:
            min = 0
        try:
            max = base_queryset.filter(date__gt=datetime).order_by('date')[:1][0][distance_field]
        except:
            max = sys.maxint
        
        return (min, max)

class MaintenanceAction(TimeStampedModel):

    log = models.ForeignKey(MaintenanceLog)

    date = models.DateField()
    mileage = models.DecimalField(_('mileage'), decimal_places=2, max_digits=8)
    mileage_km = models.DecimalField('mileage (kilometers)', decimal_places=2, max_digits=8)
    description = models.CharField(max_length=128)
    notes = models.TextField(null=True, blank=True)
    
    objects = MaintenanceActionManager()
    
    class Meta:
        ordering = ('-mileage', '-date')

    def save(self):
        # rev the modified date on the MaintenanceLog if we're editing an editing action
        #self.log.save()
        if get_current_distance_unit() == MILES:
            self.mileage_km = decimal.Decimal(self.mileage) * KILOMETERS_PER_MILE
        else:
            self.mileage = decimal.Decimal(self.mileage_km) / KILOMETERS_PER_MILE
        super(MaintenanceAction, self).save()
    
    def __unicode__(self):
        return '%s, %s: %s' % (self.date, self.mileage, self.description)

class MaintenanceExpense(models.Model):
    
    action = models.ForeignKey(MaintenanceAction)
    
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    description = models.CharField(max_length=128, verbose_name=_('expense description'), default='Total Invoice Amount')

    def save(self):
        # rev the modified date on the MaintenanceLog
        self.log.save()
        super(MaintenanceAction, self).save()
    
    def __unicode__(self):
        return '$%s - %s' % (self.amount, self.description)

FUEL_TYPE_CHOICES = (
    (0, _('Regular Unleaded')),
    (1, _('Premium Unleaded')),
    (2, _('Regular Unleaded (10% Ethanol)')),
    (3, _('Premium Unleaded (10% Ethanol)')),
    (4, _('E85')),
    (5, _('Diesel')),
    (6, _('Biodiesel')),
)
class FillupAction(MaintenanceAction):
    
    fuel_type = models.IntegerField(choices=FUEL_TYPE_CHOICES)
    #fuel_units = models.IntegerField(choices=FUEL_UNIT_CHOICES)
    gallons = models.DecimalField(decimal_places=8, max_digits=16)
    liters = models.DecimalField(decimal_places=8, max_digits=16)
    
    #distance_units = models.IntegerField(choices=DISTANCE_UNIT_CHOICES)
    miles = models.DecimalField(_('tank miles'), decimal_places=2, max_digits=8)
    kilometers = models.DecimalField(_('tank kilometers'), decimal_places=2, max_digits=8)
    
    def get_economy(self, distance_units=None, volume_units=None):
        if not volume_units:
            volume_units = get_current_volume_unit()
        if not distance_units:
            distance_units = get_current_distance_unit()
        
        economy = 0
        if distance_units == MILES:
            economy = decimal.Decimal(self.miles)
        else:
            economy = decimal.Decimal(self.kilometers)
        if volume_units == GALLONS:
            economy = economy / decimal.Decimal(self.gallons)
        else:
            economy = economy / decimal.Decimal(self.liters)
        return economy
    
    def save(self):
        """
        Save in all units to allow faster lookups, and
        easier inclusion of both in reporting functions.
        """
        if get_current_volume_unit() == GALLONS:
            self.liters = decimal.Decimal(self.gallons) * LITERS_PER_GALLON
        else:
            self.gallons = decimal.Decimal(self.liters) / LITERS_PER_GALLON
        
        if get_current_distance_unit() == MILES:
            self.kilometers = decimal.Decimal(self.miles) * KILOMETERS_PER_MILE
        else:
            self.miles = decimal.Decimal(self.kilometers) / KILOMETERS_PER_MILE
        
        # Description will just be "fill up"
        self.description = 'Fuel fill-up'
        
        super(FillupAction, self).save()

ACTION_TYPE_MODELS = (
    (0, MaintenanceAction),
    (1, FillupAction),
)
ACTION_TYPE_STRINGS = (
    (0, 'General Maintenance'),
    (1, 'Fuel Fill-up'),
)
def id_for(choices, value):
    for choice in choices:
        if choice[1] == value:
            return choice[0]
    return None
