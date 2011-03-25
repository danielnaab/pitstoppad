from csv import reader
from datetime import datetime
import os, os.path, sys, urllib, zipfile

from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.db.models import DateField, signals

from field_mappings import *
from vehicle import models

THIS_DIR = os.getcwd() + '/vehicle/'

def add_attribute(vehicle, headers, field, field_index):
    """
    Adds non-empty fields to the Vehicle model.
    Handles converting a CSV field to a format suitable to the Django ORM.
    """
    
    # some fields have extra whitespace that is screwing things up... remove it
    field = field.strip()
    
    if field and len(field) != 0:
        field_name = headers[field_index]
        
        if field_name == 'release_date':
            try:
                field = datetime.strptime(field, '%d-%b-%y')
            except ValueError:
                field = datetime.strptime(field, '%m/%d/%y')
        elif field_name == 'drive_axle_type':
            if field == 'F' or field == 'Front-Wheel Drive':
                field = models.FRONT_WHEEL_DRIVE
            elif field == 'R' or field == 'Rear-Wheel Drive':
                field = models.REAR_WHEEL_DRIVE
            elif field == '4' or field == '4-Wheel or All-Wheel Drive':
                field = models.FOUR_WHEEL_DRIVE
            else:
                raise Exception, 'Unknown drive_axle type: %s' % (field)
        elif field_name == 'fuel_type':
            if field == 'R' or field == 'Regular': field = models.REGULAR
            elif field == 'P' or field == 'Premium': field = models.PREMIUM
            elif field == 'D' or field == 'Diesel': field = models.DIESEL
            elif field == 'C' or field == 'CNG': field = models.CNG
            elif field == 'E' or field == 'Gasoline or E85': field = models.E85
            elif field == 'Premium or E85': field = models.E85_OR_PREMIUM
            elif field == 'Gasoline or natural gas': field = models.GAS_OR_CNG
            elif field == 'Gasoline or propane': field = models.GAS_OR_PROPANE
            elif field == 'El' or field == 'Electricity': field = models.ELECTRICITY
            
            else: raise Exception, 'Unknown fuel_type: %s' % (field)
        elif field_name == 'gas_guzzler' or field_name == 'turbocharger' or field_name == 'supercharger':
            if len(field) > 0: field = True
            else: field = False
        elif field_name == 'vehicle_class':
            found = False
            for v_class in VEHICLE_CLASS_MAPPINGS:
                if v_class[1] == field:
                    field = v_class[0]
                    found = True
        elif field_name == 'transmission':
            found = False
            for v_class in TRANSMISSION_STRING_MAPPINGS:
                if v_class[2] == field:
                    field = v_class[0]
                    found = True
                    
                    # we also need to set the speed... this breaks the flow, but just hack it in here:
                    vehicle.transmission_speed = v_class[1]
            
            if not found: raise Exception, 'Unknown transmission string: "%s"' % field
                    
        setattr(vehicle, headers[field_index], field)

def add_csv_files():
    """ Paths to spreadsheets from http://www.fueleconomy.gov/feg/download.shtml
        Don't use these; use DBF from epa instead.
    paths = (
        (2009, 'bin/2009/2009_FE_guide for DOE_ALL-rel dates-no-sales-8-28-08download.csv', epa_2006_to_2009),
        (2008, 'bin/2008/2008_FE_guide_ALL_rel_dates_-no sales-for DOE-5-1-08.csv', epa_2006_to_2009),
        (2007, 'bin/2007/2007_FE_guide_ALL_no_sales_May_01_2007.csv', epa_2006_to_2009),
        (2006, 'bin/2006/2006_FE_Guide_14-Nov-2005_download.csv', epa_2006_to_2009),
        (2005, 'bin/2005/guide2005-2004oct15.csv', epa_1998_to_2005),
        (2004, 'bin/2004/gd04-Feb1804-RelDtFeb20.csv', epa_1998_to_2005),
        (2003, 'bin/2003/guide_2003_feb04-03b.csv', epa_1998_to_2005),
        (2002, 'bin/2002/guide_jan28.csv', epa_1998_to_2005),
        (2001, 'bin/2001/01guide0918.csv', epa_1998_to_2005),
        (2000, 'bin/2000/G6080900.csv', epa_1998_to_2005),
        # USE THIS?  NEEDS TO BE EDITED FIRST:
        #(2000, 'bin/AFV0803.csv', epa_1998_to_2005),
        (1999, 'bin/1999/99guide6.csv', epa_1998_to_2005),
        (1998, 'bin/1998/98guide6.csv', epa_1998_to_2005),
    """
    paths = (
        (None, 'bin/1985_2009mpg10282009.csv', epa_dbf_1985_to_2009),
    )
    for year, path, field_conversions in paths:
        print '***** Adding from file %s' % (path)
        fh = open(THIS_DIR + path, 'rUb')
        table = reader(fh)
    
        header = table.next()
        headers = []
        for columnIndex, column in enumerate(header):
            headers.append(field_conversions[column])
        
        for row_index, row in enumerate(table):
            # new vehicle
            vehicle = models.EPAVehicle(year=year)
            
            # if field exists in csv, add it
            for field_index, field in enumerate(row):
                # if headers[field_index] is None, we are to ignore it
                if headers[field_index]:
                    add_attribute(vehicle, headers, field, field_index)
        
            print 'Saving row %i' % (row_index)
            vehicle.save()
    
        fh.close()
        del table


class Command(NoArgsCommand):
    help = "Import EPA Vehicle database into current DB."
    
    def handle_noargs(self, **options):
        """Import EPA Vehicle database into current DB."""
        add_csv_files()
