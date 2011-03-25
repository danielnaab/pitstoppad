from csv import reader
from datetime import datetime
import os, os.path, sys, urllib, zipfile

from django.db.models import DateField, signals

import vehicle.models

from commands.field_mappings import *

EPA_URLS = (
    ('http://www.fueleconomy.gov/feg/epadata/09data.zip', 2009),
    ('http://www.fueleconomy.gov/feg/epadata/08data.zip', 2008),
    ('http://www.fueleconomy.gov/feg/epadata/07data.zip', 2007),
    ('http://www.fueleconomy.gov/feg/epadata/06data.zip', 2006),
    ('http://www.fueleconomy.gov/feg/epadata/05data.zip', 2005),
    ('http://www.fueleconomy.gov/feg/epadata/04data.zip', 2004),
    ('http://www.fueleconomy.gov/feg/epadata/03data.zip', 2003),
    ('http://www.fueleconomy.gov/feg/epadata/02data.zip', 2002),
    ('http://www.fueleconomy.gov/feg/epadata/01data.zip', 2001),
    ('http://www.fueleconomy.gov/feg/epadata/00data.zip', 2000),
    ('http://www.fueleconomy.gov/feg/epadata/99guide.zip', 1999),
    ('http://www.fueleconomy.gov/feg/epadata/98guide6.zip', 1998),
    ('http://www.fueleconomy.gov/feg/epadata/97mfgui.zip', 1997),
    ('http://www.fueleconomy.gov/feg/epadata/96mfgui.zip', 1996),
    ('http://www.fueleconomy.gov/feg/epadata/95mfgui.zip', 1995),
    ('http://www.fueleconomy.gov/feg/epadata/94mfgui.zip', 1994),
    ('http://www.fueleconomy.gov/feg/epadata/93mfgui.zip', 1993),
    ('http://www.fueleconomy.gov/feg/epadata/92mfgui.zip', 1992),
    ('http://www.fueleconomy.gov/feg/epadata/91mfgui.zip', 1991),
    ('http://www.fueleconomy.gov/feg/epadata/90mfgui.zip', 1990),
    ('http://www.fueleconomy.gov/feg/epadata/89mfgui.zip', 1989),
    ('http://www.fueleconomy.gov/feg/epadata/88mfgui.zip', 1988),
    ('http://www.fueleconomy.gov/feg/epadata/87mfgui.zip', 1987),
    ('http://www.fueleconomy.gov/feg/epadata/86mfgui.zip', 1986),
    ('http://www.fueleconomy.gov/feg/epadata/85mfgui.zip', 1985),
    ('http://www.fueleconomy.gov/feg/epadata/84mfgui.zip', 1984),
    ('http://www.fueleconomy.gov/feg/epadata/83data.zip', 1983),
    ('http://www.fueleconomy.gov/feg/epadata/82data.zip', 1982),
    ('http://www.fueleconomy.gov/feg/epadata/81data.zip', 1981),
    ('http://www.fueleconomy.gov/feg/epadata/80data.zip', 1980),
    ('http://www.fueleconomy.gov/feg/epadata/79data.zip', 1979),
    ('http://www.fueleconomy.gov/feg/epadata/78data.zip', 1978),
)

def unzip_epa_data():
    for year in EPA_URLS:
        filename = './bin/%i.zip' % year[1]
        folder = './bin/%i' % year[1]
        print 'Unzipping %s into %s...' % (filename, folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        os.popen4('unzip %s -d %s' % (filename, folder))

def download_epa_data():
    for url in EPA_URLS:
        filename = './bin/%i.zip' % url[1]
        print 'Getting %s as %s...' % (url[0], filename)
        urllib.urlretrieve(url[0], filename)

def create_indices():
    print '*** Creating indices...'
    from django.db import connection
    cursor = connection.cursor()

    # make/model is the primary sort order, so create an index on both
    cursor.execute('CREATE INDEX index_make_model ON vehicle_epavehicle (model, manufacturer)')
    
    # create index on individual columns.  these are the fields exposed in the vehicle search interface.
    index_columns = ['year', 'manufacturer', 'model', 'transmission', 'transmission_speed', 'vehicle_class']
    for column in index_columns:
        print '***** Index: ' + column
        cmd = "CREATE INDEX index_%s ON vehicle_epavehicle (%s)" % (column, column)
        cursor.execute(cmd)

if __name__ == '__main__':
    if not os.path.isdir('./bin'):
        os.mkdir('./bin')
    download_epa_data()
    unzip_epa_data()
