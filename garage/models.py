from django.db import models
from django.contrib.auth.models import User

from log.models import MaintenanceLog, MaintenanceAction, FillupAction
from units.middleware import current_fuel_economy_units
from vehicle.models import EPAVehicle

class Garage(models.Model):
    user = models.OneToOneField(User)
    
    @models.permalink
    def get_absolute_url(self):
        return ('garage_view_garage', [str(self.user)])
    
    def average_fuel_economy_string(self):
        # TODO: this can be made more efficient.
        fillups = FillupAction.objects.filter(log__garagevehicle__garage=self)
        total_economy = 0
        average_economy = 0
        for fillup in fillups:
            total_economy = total_economy + fillup.get_economy()
        if len(fillups) is not 0:
            average_economy = total_economy / len(fillups)
        return '%s %s' % (average_economy, current_fuel_economy_units())
    
    def total_mileage_logged_string(self):
        return '(not implemented) miles'
    
    def total_cost_logged_string(self):
        #MaintenanceAction.objects.filter(log__garagevehicle__garage=self).values('cost')
        return '$(not implemented)'

#
# Handle creating a garage instance when users are created/deleted.
#
def user_post_save(sender, instance, **kwargs):
    garage, new = Garage.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, sender=User)


class GarageVehicle(models.Model):
    vehicle = models.ForeignKey(EPAVehicle)
    garage = models.ForeignKey(Garage)
    log = models.OneToOneField(MaintenanceLog, null=True, blank=True)
    
    purchase_date = models.DateField(null=True, blank=True)
    # TODO: make this a decimal.  we're not doing anything with it yet and we don't handle currency,
    # so just a CharField for now
    #purchase_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    purchase_price = models.CharField(max_length=12, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    def __unicode__(self):
        return str(self.vehicle)
    
    def save(self):
        if self.log is None:
            log = MaintenanceLog(vehicle=self.vehicle, user=self.garage.user)
            log.save()
            self.log = log
        super(GarageVehicle, self).save()

class FollowingManager(models.Manager):
    
    def is_following(self, follower, followed):
        try:
            following = self.get(follower=follower, followed=followed)
            return True
        except Following.DoesNotExist:
            return False
    
    def follow(self, follower, followed):
        if follower != followed and not self.is_following(follower, followed):
            Following(follower=follower, followed=followed).save()
    
    def unfollow(self, follower, followed):
        try:
            following = self.get(follower=follower.id, followed=followed.id)
            following.delete()
        except Following.DoesNotExist:
            pass
    
    def toggle_follow(self, follower, followed):
        if self.is_following(follower, followed):
            self.unfollow(follower, followed)
        else:
            self.follow(follower, followed)

class Following(models.Model):
    follower = models.ForeignKey(Garage, related_name="followed")
    followed = models.ForeignKey(Garage, related_name="followers")
    
    objects = FollowingManager()
