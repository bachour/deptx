# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'RequisitionElement'
        db.delete_table(u'assets_requisitionelement')

        # Deleting model 'TaskElement'
        db.delete_table(u'assets_taskelement')

        # Adding model 'Requisition'
        db.create_table(u'assets_requisition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
        ))
        db.send_create_signal(u'assets', ['Requisition'])

        # Adding model 'Task'
        db.create_table(u'assets_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('serial', self.gf('django.db.models.fields.CharField')(default='16ae1426-e979-11e2-a495-14109fe17ee1', max_length=36)),
        ))
        db.send_create_signal(u'assets', ['Task'])


    def backwards(self, orm):
        # Adding model 'RequisitionElement'
        db.create_table(u'assets_requisitionelement', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=16, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'assets', ['RequisitionElement'])

        # Adding model 'TaskElement'
        db.create_table(u'assets_taskelement', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('serial', self.gf('django.db.models.fields.CharField')(default='c209d1d4-e974-11e2-b7c8-14109fe17ee1', max_length=36)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'assets', ['TaskElement'])

        # Deleting model 'Requisition'
        db.delete_table(u'assets_requisition')

        # Deleting model 'Task'
        db.delete_table(u'assets_task')


    models = {
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'16aff5e6-e979-11e2-bb3c-14109fe17ee1'", 'max_length': '36'}),
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