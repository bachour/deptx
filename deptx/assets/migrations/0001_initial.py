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
            ('serial', self.gf('django.db.models.fields.CharField')(default='cfbede4a-0a6f-11e3-8388-14109fe17ee1', max_length=36)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('isAdministrative', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'assets', ['Unit'])

        # Adding model 'Requisition'
        db.create_table(u'assets_requisition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='cfba914c-0a6f-11e3-b039-14109fe17ee1', max_length=36)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('category', self.gf('django.db.models.fields.IntegerField')()),
            ('trust', self.gf('django.db.models.fields.IntegerField')(default=25)),
            ('isInitial', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'assets', ['Requisition'])

        # Adding model 'Task'
        db.create_table(u'assets_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('serial', self.gf('django.db.models.fields.CharField')(default='cfbf354f-0a6f-11e3-9a24-14109fe17ee1', max_length=36)),
            ('trust', self.gf('django.db.models.fields.IntegerField')(default=25)),
        ))
        db.send_create_signal(u'assets', ['Task'])

        # Adding model 'Mission'
        db.create_table(u'assets_mission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'assets', ['Mission'])

        # Adding model 'Case'
        db.create_table(u'assets_case', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('mission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Mission'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
            ('serial', self.gf('django.db.models.fields.SlugField')(default='cfbef52b-0a6f-11e3-a59d-14109fe17ee1', max_length=36)),
        ))
        db.send_create_signal(u'assets', ['Case'])

        # Adding model 'Document'
        db.create_table(u'assets_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='cfbf00e3-0a6f-11e3-9cdc-14109fe17ee1', max_length=36)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Task'])),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'])),
        ))
        db.send_create_signal(u'assets', ['Document'])


    def backwards(self, orm):
        # Deleting model 'Unit'
        db.delete_table(u'assets_unit')

        # Deleting model 'Requisition'
        db.delete_table(u'assets_requisition')

        # Deleting model 'Task'
        db.delete_table(u'assets_task')

        # Deleting model 'Mission'
        db.delete_table(u'assets_mission')

        # Deleting model 'Case'
        db.delete_table(u'assets_case')

        # Deleting model 'Document'
        db.delete_table(u'assets_document')


    models = {
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'cfc05a7a-0a6f-11e3-8c9d-14109fe17ee1'", 'max_length': '36'})
        },
        u'assets.document': {
            'Meta': {'object_name': 'Document'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'cfc065ba-0a6f-11e3-8af7-14109fe17ee1'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Task']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'cfc02b54-0a6f-11e3-9a97-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'cfc08ce8-0a6f-11e3-9c15-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'cfc044a3-0a6f-11e3-805f-14109fe17ee1'", 'max_length': '36'})
        }
    }

    complete_apps = ['assets']