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
            ('serial', self.gf('django.db.models.fields.CharField')(default='573874ba-eafe-11e2-9ab6-14109fe17ee1', max_length=36)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('isAdministrative', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'assets', ['Unit'])

        # Adding model 'Requisition'
        db.create_table(u'assets_requisition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='5737a711-eafe-11e2-951d-14109fe17ee1', max_length=36)),
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
            ('serial', self.gf('django.db.models.fields.CharField')(default='57388b0a-eafe-11e2-aaf0-14109fe17ee1', max_length=36)),
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
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5738e4f3-eafe-11e2-b6fe-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5739103a-eafe-11e2-a080-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5738fad4-eafe-11e2-af1d-14109fe17ee1'", 'max_length': '36'})
        }
    }

    complete_apps = ['assets']