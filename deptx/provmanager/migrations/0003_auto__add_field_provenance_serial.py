# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Provenance.serial'
        db.add_column(u'provmanager_provenance', 'serial',
                      self.gf('django.db.models.fields.SlugField')(default='34e0a0a6-1ae5-11e3-8fc2-14109fe17ee1', max_length=36),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Provenance.serial'
        db.delete_column(u'provmanager_provenance', 'serial')


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'34e20a02-1ae5-11e3-bb02-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['provmanager']