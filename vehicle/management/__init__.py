from django.db.models import signals

from vehicle import models

def create_indices():
    print '*** Creating indices...'
    from django.db import connection
    from django.db.utils import DatabaseError
    cursor = connection.cursor()

    # make/model is the primary sort order, so create an index on both
    try:
        cursor.execute('CREATE INDEX index_make_model ON vehicle_epavehicle (model, manufacturer)')
        print 'Index `index_make_model` created'
    except DatabaseError, e:
        print 'Index index_make_model already exists'
    
    # create index on individual columns.  these are the fields exposed in the vehicle search interface.
    index_columns = ['year', 'manufacturer', 'model', 'transmission', 'transmission_speed', 'vehicle_class']
    for column in index_columns:
        cmd = "CREATE INDEX index_%s ON vehicle_epavehicle (%s)" % (column, column)
        try:
            cursor.execute(cmd)
            print 'Index `%s` created' % column
        except DatabaseError, e:
            print 'Index index_%s already exists' % column

def init_data(sender, **kwargs):
    create_indices()

signals.post_syncdb.connect(init_data, sender=models)
