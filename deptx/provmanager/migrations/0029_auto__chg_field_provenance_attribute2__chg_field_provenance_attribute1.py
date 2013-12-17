# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Provenance.attribute2'
        db.alter_column(u'provmanager_provenance', 'attribute2', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Provenance.attribute1'
        db.alter_column(u'provmanager_provenance', 'attribute1', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Provenance.name'
        db.alter_column(u'provmanager_provenance', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

    def backwards(self, orm):

        # Changing field 'Provenance.attribute2'
        db.alter_column(u'provmanager_provenance', 'attribute2', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'Provenance.attribute1'
        db.alter_column(u'provmanager_provenance', 'attribute1', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'Provenance.name'
        db.alter_column(u'provmanager_provenance', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'serial': ('django.db.models.fields.SlugField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['provmanager']