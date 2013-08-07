# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Mission'
        db.create_table(u'assets_mission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'assets', ['Mission'])


    def backwards(self, orm):
        # Deleting model 'Mission'
        db.delete_table(u'assets_mission')


    models = {
        u'assets.document': {
            'Meta': {'object_name': 'Document'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'a6d820e1-f93d-11e2-b3c3-14109fe17ee1'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Task']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'assets.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'document': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.Document']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagefile': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pdBundle': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['persistence.PDBundle']", 'unique': 'True'})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'a6d8004c-f93d-11e2-a5a9-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'a6d7f373-f93d-11e2-9ce5-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'a6d7a7dc-f93d-11e2-b7c9-14109fe17ee1'", 'max_length': '36'})
        },
        u'persistence.pdbundle': {
            'Meta': {'object_name': 'PDBundle', '_ormbases': [u'persistence.PDRecord']},
            u'pdrecord_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['persistence.PDRecord']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'persistence.pdrecord': {
            'Meta': {'object_name': 'PDRecord'},
            'asserted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references'", 'symmetrical': 'False', 'through': u"orm['persistence.RecordAttribute']", 'to': u"orm['persistence.PDRecord']"}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_records'", 'null': 'True', 'to': u"orm['persistence.PDBundle']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rec_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'rec_type': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True'})
        },
        u'persistence.recordattribute': {
            'Meta': {'object_name': 'RecordAttribute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prov_type': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_records'", 'to': u"orm['persistence.PDRecord']"}),
            'value': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_records'", 'to': u"orm['persistence.PDRecord']"})
        }
    }

    complete_apps = ['assets']