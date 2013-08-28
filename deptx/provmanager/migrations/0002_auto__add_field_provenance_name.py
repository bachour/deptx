# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Provenance.name'
        db.add_column(u'provmanager_provenance', 'name',
                      self.gf('django.db.models.fields.CharField')(default='random', max_length=50),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Provenance.name'
        db.delete_column(u'provmanager_provenance', 'name')


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['provmanager']