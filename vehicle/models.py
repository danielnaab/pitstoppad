from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from managers import *

class Vehicle(models.Model):
    # Stuff in EPA (and other?) data here in the future
    make_and_model = models.CharField(max_length=64, default='make and model')
    
    def __unicode__(self):
        return '%s' % (self.make_and_model)

FRONT_WHEEL_DRIVE = 0
REAR_WHEEL_DRIVE = 1
FOUR_WHEEL_DRIVE = 2
DRIVE_SYSTEMS = (
    (FRONT_WHEEL_DRIVE, 'Front-wheel Drive'),
    (REAR_WHEEL_DRIVE, 'Rear-wheel Drive'),
    (FOUR_WHEEL_DRIVE, '4-wheel Drive'),
)

REGULAR = 0
PREMIUM = 1
DIESEL = 2
E85 = 3
E85_OR_PREMIUM = 4
GAS_OR_CNG = 5
CNG = 6
GAS_OR_PROPANE = 7
ELECTRICITY = 8
FUEL_TYPES = (
    (REGULAR, 'Regular Gasoline (87 Octane)'), # R
    (PREMIUM, 'Premium Gasoline (92-93 Octane)'), #P
    (DIESEL, 'Diesel'), # D
    (E85, 'Flexfuel - Gasoline or E85'), # E
    (E85_OR_PREMIUM, 'Flexfuel - Premium or E85'),
    (GAS_OR_CNG, 'Gasoline or Natural Gas'),
    (CNG, 'Compressed Natural Gas'), # C
    (GAS_OR_CNG, 'Gasoline or Propane'),
    (ELECTRICITY, 'Electricity'), # El
)

# Note: management.py also uses these strings for matching during data import.
# If the strings are changed, management.py must be updated to match the original strings.
VEHICLE_CLASSES = (
    (0, 'Car - Subcompact'),
    (1, 'Car - Compact'),
    (2, 'Car - Midsize'),
    (3, 'Car - Large'),
    (4, 'Minivan'),
    (5, 'Pickup Truck - Small'),
    (6, 'Pickup Truck - Standard'),
    (7, 'Station Wagon - Small'),
    (8, 'Station Wagon - Midsize'),
    (9, 'Station Wagon - Midsize-Large'),
    (10, 'SPV (Special Purpose Vehicle)'),
    (11, 'SUV - (Sport Utility Vehicle)'),
    (12, 'Van'),
)

# Note: management.py also uses these strings for matching during data import.
# If the strings are changed, management.py must be updated to match the original strings.
NO_TRANSMISSION = 0
AUTOMATIC = 1
MANUAL = 2
TRANSMISSION_OPTIONS = (
    (NO_TRANSMISSION, 'No Transmission'),
    (AUTOMATIC, 'Automatic'),
    (MANUAL, 'Manual'),
)
VBR = -1
TRANSMISSION_SPEED_OPTIONS = (
    (VBR, 'Variable Gear Ratios'),
    (0, 'None'),
    (1, 'Single-speed'),
    (2, 'Two-speed'),
    (3, 'Three-speed'),
    (4, 'Four-speed'),
    (5, 'Five-speed'),
    (6, 'Six-speed'),
    (7, 'Seven-speed'),
    (8, 'Eight-speed'),
)

EPAVEHICLE_FIELD_SLUG_MAPPING = (
    ('model', 'model_slug'),
    ('manufacturer', 'manufacturer_slug'),
)

EPA_VEHICLE_YEARS = [(0, '')] + [(year, str(year)) for year in range(1985, datetime.now().year+1)]

class EPAVehicle(models.Model):

    objects = EPAVehicleManager()
    
    # field to delete?
    fuel_price = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    index_number = models.IntegerField(blank=True, null=True)
    
    # delete?  these three are in the spreadsheets but not the DBF
    class_code = models.IntegerField(blank=True, null=True) # sort vehicle_class with this field (?)
    release_date = models.DateField(blank=True, null=True)
    test_method = models.CharField(max_length=32, blank=True, null=True)
    
    vehicle_class = models.IntegerField(choices=VEHICLE_CLASSES, blank=True, null=True)
    
    year = models.IntegerField() # min_value=1985, max_value=datetime.now().year+1
    
    manufacturer = models.CharField(max_length=32)
    model = models.CharField(max_length=32)
    displacement_in_liters = models.DecimalField(decimal_places=1, max_digits=3, blank=True, null=True)
    number_of_cylinders = models.IntegerField(blank=True, null=True)
    transmission = models.IntegerField(choices=TRANSMISSION_OPTIONS, blank=True, null=True, default=NO_TRANSMISSION)
    transmission_speed = models.IntegerField(choices=TRANSMISSION_SPEED_OPTIONS, blank=True, null=True, default=0)
    drive_axle_type = models.IntegerField(choices=DRIVE_SYSTEMS, blank=True, null=True)
    city_mpg_guide = models.IntegerField(max_length=32, blank=True, null=True)
    highway_mpg_guide = models.IntegerField(blank=True, null=True)
    combined_mpg_guide = models.IntegerField(blank=True, null=True)
    unrated_city_epa = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True)
    unrated_hwy_epa = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True)
    unrated_combined_epa = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True)
    fuel_type = models.IntegerField(choices=FUEL_TYPES, blank=True, null=True)
    gas_guzzler = models.NullBooleanField(blank=True, null=True)
    turbocharger = models.NullBooleanField(blank=True, null=True)
    supercharger = models.NullBooleanField(blank=True, null=True)
    two_door_passenger_volume = models.IntegerField(blank=True, null=True)
    two_door_luggage_volume = models.IntegerField(blank=True, null=True)
    four_door_passenger_volume = models.IntegerField(blank=True, null=True)
    four_door_luggage_volume = models.IntegerField(blank=True, null=True)
    hatchback_passenger_volume = models.IntegerField(blank=True, null=True)
    hatchback_luggage_volume = models.IntegerField(blank=True, null=True)
    annual_fuel_cost = models.IntegerField(blank=True, null=True)
    engine_block = models.CharField(max_length=32, blank=True, null=True)
    transmission_description = models.CharField(max_length=32, blank=True, null=True)
    valves_per_cylinder = models.IntegerField(blank=True, null=True)

    # fields only in the DBF file.  few vehicles have available - not sure what they are:
    #CITYA,N,11,0 HIGHWAYA,N,11,0 COMBINEDA,N,11,0 UCITYA,N,8,4 UHIGHWAYA,N,8,4 UCOMBINEDA,N,8,4
    citya = models.DecimalField(decimal_places=0, max_digits=11, blank=True, null=True)
    highwaya = models.DecimalField(decimal_places=0, max_digits=11, blank=True, null=True)
    combineda = models.DecimalField(decimal_places=0, max_digits=11, blank=True, null=True)
    ucitya = models.DecimalField(decimal_places=4, max_digits=8, blank=True, null=True)
    uhighwaya = models.DecimalField(decimal_places=4, max_digits=8, blank=True, null=True)
    ucombineda = models.DecimalField(decimal_places=4, max_digits=8, blank=True, null=True)
    
    # 08 fields: CITY08,N,3,0 HIGHWAY08,N,3,0 COMB08,N,3,0 CITYA08,N,3,0 HIGHWAYA08,N,3,0 COMBA08,N,3,0 COST08,N,5,0 COSTA08,N,5,0
    city08 = models.IntegerField(blank=True, null=True)
    highway08 = models.IntegerField(blank=True, null=True)
    combined08 = models.IntegerField(blank=True, null=True)
    ucitya08 = models.IntegerField(blank=True, null=True)
    uhighwaya08 = models.IntegerField(blank=True, null=True)
    ucombineda08 = models.IntegerField(blank=True, null=True)
    # these same as annual_fuel_cost (?)
    cost08 = models.IntegerField(blank=True, null=True)
    costa08 = models.IntegerField(blank=True, null=True)
    
    # slugs...
    model_slug = models.CharField(max_length=32, blank=True, null=True)
    manufacturer_slug = models.CharField(max_length=32, blank=True, null=True)
    
    def save(self):
        from django.template.defaultfilters import slugify
        self.model_slug = slugify(self.model)
        self.manufacturer_slug = slugify(self.manufacturer)
        super(EPAVehicle, self).save()
    
    def display_passenger_volume(self):
        # only one of the volume field is set, so just sum them up
        return str(self.two_door_passenger_volume + self.four_door_passenger_volume + self.hatchback_passenger_volume)
    
    def display_luggage_volume(self):
        # only one of the volume field is set, so just sum them up
        return str(self.two_door_luggage_volume + self.four_door_luggage_volume + self.hatchback_luggage_volume)
        
    def year_make_model(self, convert_spaces_to=None):
        str = '%s %s %s' % (self.year, self.manufacturer, self.model)
        if convert_spaces_to: str = str.replace(' ', convert_spaces_to)
        return str
    
    def get_absolute_url(self):
        return reverse('vehicle_view', args=[self.year_make_model('-'), self.id])
    
    def get_add_to_garage_url(self):
        return '%s?add_vehicle=%s' % (reverse('garage_my_garage'), self.id)
    
    def __unicode__(self):
        return self.year_make_model()
