from django.db.models import signals

from vehicle import models

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

def init_data(sender, **kwargs):
    create_indices()

signals.post_syncdb.connect(init_data, sender=models)
