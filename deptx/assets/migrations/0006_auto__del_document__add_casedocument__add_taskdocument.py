# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Document'
        db.delete_table(u'assets_document')

        # Adding model 'CaseDocument'
        db.create_table(u'assets_casedocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='541760c7-0ffe-11e3-9bf0-14109fe17ee1', max_length=36)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'], null=True, blank=True)),
        ))
        db.send_create_signal(u'assets', ['CaseDocument'])

        # Adding model 'TaskDocument'
        db.create_table(u'assets_taskdocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='541698c7-0ffe-11e3-985e-14109fe17ee1', max_length=36)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Task'], null=True, blank=True)),
        ))
        db.send_create_signal(u'assets', ['TaskDocument'])


    def backwards(self, orm):
        # Adding model 'Document'
        db.create_table(u'assets_document', (
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'], null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='d3728426-0ffc-11e3-84d4-14109fe17ee1', max_length=36)),
            ('provenance', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['provmanager.Provenance'], unique=True, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Task'], null=True, blank=True)),
        ))
        db.send_create_signal(u'assets', ['Document'])

        # Deleting model 'CaseDocument'
        db.delete_table(u'assets_casedocument')

        # Deleting model 'TaskDocument'
        db.delete_table(u'assets_taskdocument')


    models = {
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'541b55b5-0ffe-11e3-9724-14109fe17ee1'", 'max_length': '36'})
        },
        u'assets.casedocument': {
            'Meta': {'object_name': 'CaseDocument'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['provmanager.Provenance']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'541b1b1e-0ffe-11e3-a39c-14109fe17ee1'", 'max_length': '36'}),
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
            'serial': ('django.db.models.fields.CharField', [], {'default': "'541b31c7-0ffe-11e3-b267-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'541b69fa-0ffe-11e3-b872-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.taskdocument': {
            'Meta': {'object_name': 'TaskDocument'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['provmanager.Provenance']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'541b03de-0ffe-11e3-8faa-14109fe17ee1'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Task']", 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'541b7670-0ffe-11e3-84d7-14109fe17ee1'", 'max_length': '36'})
        },
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['assets']