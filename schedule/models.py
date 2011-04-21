from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

class Vehicle(models.Model):
    # Stuff in EPA (and other?) data here in the future
    make_and_model = models.CharField(max_length=64)
    
    def __unicode__(self):
        return '%s' % (self.make_and_model)

class ScheduleManager(models.Manager):
    
    def for_user(self, username):
        return self.all().filter(created_by__username=username)
    
class Schedule(TimeStampedModel):
    # TimeStampedModel includes 'created' and 'modified' fields
    created_by = models.ForeignKey(User)
    description = models.CharField(max_length=128)
    
    objects = ScheduleManager()
    
    def __unicode__(self):
        return '%s, %s' % (self.description, self.created_by.username)

DAYS = 0
MONTHS = 1
YEARS = 2
AGE_UNITS = (
    (DAYS,      'Days'),
    (MONTHS,    'Months'),
    (YEARS,     'Years'),
)
class ScheduleItem(models.Model):
    
    schedule = models.ForeignKey(Schedule)
    
    start_at_mileage = models.IntegerField(default=0)
    start_at_age_units = models.IntegerField(choices=AGE_UNITS, default=MONTHS)     # used by save function to convert age to days
                                                                                    #   and remember what unit to display to user.
    start_at_age = models.FloatField(default=0)                                     # specified in days, eg 1 year = 365.
    
    recurring_mileage = models.IntegerField(default=0)
    recurring_age_units = models.IntegerField(choices=AGE_UNITS, default=MONTHS)    # used by save function to convert age to days
                                                                                    #   and remember what unit to display to user.
    recurring_age = models.FloatField(default=0)                                    # specified in days, eg 1 year = 365.
    
    end_at_mileage = models.IntegerField(default=0)
    end_at_age = models.FloatField(default=0)
    
    def recurring_age_str(self):
        if self.recurring_age_units == DAYS:
            return '%s days' % (self.recurring_age)
        elif self.recurring_age_units == MONTHS:
            return '%s months' % (self.recurring_age*int(365/12))
        elif self.recurring_age_units == YEARS:
            return '%s years' % (self.recurring_age*365)
    
    def recurring_str(self):
        if self.recurring_mileage != 0:
            recurring = 'Every %s miles' % (self.recurring_mileage)
            if self.recurring_age:
                recurring = '%s (or %s)' % (recurring, self.recurring_age_str())
                return recurring
        elif self.recurring_age != 0:
            return 'Every %s)' % (self.recurring_age_str())
        else:
            return None
    
    def __unicode__(self):
        #ret = ''
        #recurring = None
        #if start_at_mileage != 0 or end_at_mileage != 0:
        #    ret += 'from %s to %s miles' % (start_at_mileage, end_at_mileage)
        #ret += self.recurring_str()
        return 'Starting at %s miles or %s days, every %s miles or %s days' % (self.start_at_mileage, self.start_at_age, self.recurring_mileage, self.recurring_age)

class ScheduleItemAction(models.Model):
    
    schedule_item = models.ForeignKey(ScheduleItem)
    
    description = models.CharField(max_length=128)
    notes = models.TextField()
    
    def __unicode__(self):
        return self.description
