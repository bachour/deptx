# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Provenance.graphml'
        db.add_column(u'provmanager_provenance', 'graphml',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Provenance.graphml'
        db.delete_column(u'provmanager_provenance', 'graphml')


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'graphml': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'e1c3be17-1bb5-11e3-ab1a-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['provmanager']