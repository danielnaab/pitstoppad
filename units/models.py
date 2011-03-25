import decimal

from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

GALLONS = 0
LITERS = 1
VOLUME_CHOICES = (
    (GALLONS, _('Gallons')),
    (LITERS, _('Liters')),
)
LITERS_PER_GALLON = decimal.Decimal('3.78541178')

MILES = 0
KILOMETERS = 1
DISTANCE_CHOICES = (
    (MILES, _('Miles')),
    (KILOMETERS, _('Kilometers')),
)
KILOMETERS_PER_MILE = decimal.Decimal('1.609344')

class UnitsPref(models.Model):
    user = models.ForeignKey(User, unique=True)
    volume_unit = models.IntegerField(choices=VOLUME_CHOICES, default=GALLONS)
    distance_unit = models.IntegerField(choices=DISTANCE_CHOICES, default=MILES)

    def is_english(self):
        # Volumes and distances can be set separately, but we are only "english" if both are english
        return self.volume_unit == GALLONS and self.distance_unit == MILES

    def is_metric(self):
        # Volumes and distances can be set separately, but we are only "metric" if both are metric
        return self.volume_unit == LITERS and self.distance_unit == KILOMETERS

    def __unicode__(self):
        return '(user, volume, distance): (%s, %s, %s)' % (self.user, VOLUME_CHOICES[self.volume_unit][1], DISTANCE_CHOICES[self.distance_unit][1])

def set_user_units(user, volume_unit, distance_unit):
    pref = None
    try:
        pref = UnitsPref.objects.get(user=user)
    except:
        pref = UnitsPref(user=user)
    pref.volume_unit = volume_unit
    pref.distance_unit = distance_unit
    pref.save()

def get_user_units(user):
    try:
        pref = UnitsPref.objects.get(user=user)
        return (pref.volume_unit, pref.distance_unit)
    except:
        return (GALLONS, MILES)
