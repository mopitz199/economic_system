from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    operations = [
        HStoreExtension()
    ]

# also exec psql -U admin -d template1 -c 'create extension hstore;'
