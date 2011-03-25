from django.db import models
from django.db.models import query

class EPAVehicleQuerySet(query.QuerySet):
    def distinct_values(self, *args):
        """
        Returns the distinct values for the current query.
        """
        return self.values(*args).distinct().order_by(*args)
    
    def distinct_makes(self):
        return self.distinct_values('manufacturer', 'manufacturer_slug')
    
    def distinct_models(self):
        return self.distinct_values('model', 'model_slug')
    
    def distinct_years(self):
        return self.distinct_values('year')

    def distinct_transmissions(self):
        return self.distinct_values('transmission')
    
    def distinct_transmission_speeds(self):
        return self.distinct_values('transmission_speed')

    def distinct_vehicle_classes(self):
        return self.distinct_values('vehicle_class')

class EPAVehicleManager(models.Manager):
    
    def get_query_set(self):
        return EPAVehicleQuerySet(self.model)
