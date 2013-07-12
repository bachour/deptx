# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Unit'
        db.create_table(u'assets_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'assets', ['Unit'])

        # Adding model 'Requisition'
        db.create_table(u'assets_requisition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('category', self.gf('django.db.models.fields.IntegerField')()),
            ('trust', self.gf('django.db.models.fields.IntegerField')(default=25)),
        ))
        db.send_create_signal(u'assets', ['Requisition'])

        # Adding model 'Task'
        db.create_table(u'assets_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('serial', self.gf('django.db.models.fields.CharField')(default='9ed4b138-eaf4-11e2-b591-14109fe17ee1', max_length=36)),
            ('trust', self.gf('django.db.models.fields.IntegerField')(default=25)),
        ))
        db.send_create_signal(u'assets', ['Task'])


    def backwards(self, orm):
        # Deleting model 'Unit'
        db.delete_table(u'assets_unit')

        # Deleting model 'Requisition'
        db.delete_table(u'assets_requisition')

        # Deleting model 'Task'
        db.delete_table(u'assets_task')


    models = {
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'9ed5dca3-eaf4-11e2-9e6f-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
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