# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Provenance.node1'
        db.add_column(u'provmanager_provenance', 'node1',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Provenance.attribute1'
        db.add_column(u'provmanager_provenance', 'attribute1',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Provenance.node2'
        db.add_column(u'provmanager_provenance', 'node2',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Provenance.attribute2'
        db.add_column(u'provmanager_provenance', 'attribute2',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Provenance.node1'
        db.delete_column(u'provmanager_provenance', 'node1')

        # Deleting field 'Provenance.attribute1'
        db.delete_column(u'provmanager_provenance', 'attribute1')

        # Deleting field 'Provenance.node2'
        db.delete_column(u'provmanager_provenance', 'node2')

        # Deleting field 'Provenance.attribute2'
        db.delete_column(u'provmanager_provenance', 'attribute2')


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'node2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'bab00933-1bca-11e3-8980-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['provmanager']