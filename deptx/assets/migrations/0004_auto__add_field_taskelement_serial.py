# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TaskElement.serial'
        db.add_column(u'assets_taskelement', 'serial',
                      self.gf('django.db.models.fields.CharField')(default='c207e126-e974-11e2-a5a3-14109fe17ee1', max_length=36),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TaskElement.serial'
        db.delete_column(u'assets_taskelement', 'serial')


    models = {
        u'assets.requisitionelement': {
            'Meta': {'object_name': 'RequisitionElement'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.taskelement': {
            'Meta': {'object_name': 'TaskElement'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'c209d1d4-e974-11e2-b7c8-14109fe17ee1'", 'max_length': '36'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        }
    }

    complete_apps = ['assets']