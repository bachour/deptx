# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CaseDocument'
        db.delete_table(u'assets_casedocument')

        # Deleting model 'TaskDocument'
        db.delete_table(u'assets_taskdocument')

        # Adding model 'Document'
        db.create_table(u'assets_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='e08c3407-1005-11e3-93b2-14109fe17ee1', max_length=36)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'], null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Task'], null=True, blank=True)),
        ))
        db.send_create_signal(u'assets', ['Document'])


    def backwards(self, orm):
        # Adding model 'CaseDocument'
        db.create_table(u'assets_casedocument', (
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'], null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='541b1b1e-0ffe-11e3-a39c-14109fe17ee1', max_length=36)),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
        ))
        db.send_create_signal(u'assets', ['CaseDocument'])

        # Adding model 'TaskDocument'
        db.create_table(u'assets_taskdocument', (
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='541b03de-0ffe-11e3-8faa-14109fe17ee1', max_length=36)),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Task'], null=True, blank=True)),
        ))
        db.send_create_signal(u'assets', ['TaskDocument'])

        # Deleting model 'Document'
        db.delete_table(u'assets_document')


    models = {
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'e0900b1e-1005-11e3-9f02-14109fe17ee1'", 'max_length': '36'})
        },
        u'assets.document': {
            'Meta': {'object_name': 'Document'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['provmanager.Provenance']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'e0901a51-1005-11e3-8a17-14109fe17ee1'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Task']", 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            'briefing': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'debriefing': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'e08fee5e-1005-11e3-a4ef-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'e08fb54f-1005-11e3-9e8f-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'e08fc373-1005-11e3-abfe-14109fe17ee1'", 'max_length': '36'})
        },
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['assets']