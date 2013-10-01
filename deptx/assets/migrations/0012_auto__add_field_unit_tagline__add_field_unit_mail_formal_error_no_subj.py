# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Unit.tagline'
        db.add_column(u'assets_unit', 'tagline',
                      self.gf('django.db.models.fields.CharField')(default='Prov is all around you', max_length=256),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_no_subject'
        db.add_column(u'assets_unit', 'mail_formal_error_no_subject',
                      self.gf('django.db.models.fields.TextField')(default='Your mail cannot be categorized. Please choose a subject next time.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_missing_form'
        db.add_column(u'assets_unit', 'mail_formal_error_missing_form',
                      self.gf('django.db.models.fields.TextField')(default='You did not attach a form. Please always attach a form.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_wrong_unit'
        db.add_column(u'assets_unit', 'mail_formal_error_wrong_unit',
                      self.gf('django.db.models.fields.TextField')(default='Form {{form}} cannot be processed by us. Please send it to the appropriate unit.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_wrong_form'
        db.add_column(u'assets_unit', 'mail_formal_error_wrong_form',
                      self.gf('django.db.models.fields.TextField')(default='The type of form does not match your request.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_redundant_document'
        db.add_column(u'assets_unit', 'mail_formal_error_redundant_document',
                      self.gf('django.db.models.fields.TextField')(default='You have attached an unnecessary document.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_missing_document'
        db.add_column(u'assets_unit', 'mail_formal_error_missing_document',
                      self.gf('django.db.models.fields.TextField')(default='Your report can only be processed if you attach a document.'),
                      keep_default=False)

        # Adding field 'Unit.mail_formal_error_wrong_document'
        db.add_column(u'assets_unit', 'mail_formal_error_wrong_document',
                      self.gf('django.db.models.fields.TextField')(default='Attached document {{document}} does not belong to report concerning task {{task}}.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_unfound_form'
        db.add_column(u'assets_unit', 'mail_content_error_unfound_form',
                      self.gf('django.db.models.fields.TextField')(default='Form {{form}} which you requested does not exist.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_unfound_task'
        db.add_column(u'assets_unit', 'mail_content_error_unfound_task',
                      self.gf('django.db.models.fields.TextField')(default='Task {{task}} which you requested does not exist within this unit.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_unfound_document'
        db.add_column(u'assets_unit', 'mail_content_error_unfound_document',
                      self.gf('django.db.models.fields.TextField')(default='Document {{document}} which you requested does not exist within this unit.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_existing_form'
        db.add_column(u'assets_unit', 'mail_content_error_existing_form',
                      self.gf('django.db.models.fields.TextField')(default='You already have access to form {{form}}.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_existing_task'
        db.add_column(u'assets_unit', 'mail_content_error_existing_task',
                      self.gf('django.db.models.fields.TextField')(default='You have already been assigned to task {{task}}.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_existing_document'
        db.add_column(u'assets_unit', 'mail_content_error_existing_document',
                      self.gf('django.db.models.fields.TextField')(default='You already have access to document {{document}}.'),
                      keep_default=False)

        # Adding field 'Unit.mail_content_error_unassigned_task'
        db.add_column(u'assets_unit', 'mail_content_error_unassigned_task',
                      self.gf('django.db.models.fields.TextField')(default='We could not find task {{task}} your report is about.'),
                      keep_default=False)

        # Adding field 'Unit.mail_assigning_form'
        db.add_column(u'assets_unit', 'mail_assigning_form',
                      self.gf('django.db.models.fields.TextField')(default='We have assigned form {{form}} to you.'),
                      keep_default=False)

        # Adding field 'Unit.mail_assigning_task'
        db.add_column(u'assets_unit', 'mail_assigning_task',
                      self.gf('django.db.models.fields.TextField')(default='We have assigned task {{task}} to you.'),
                      keep_default=False)

        # Adding field 'Unit.mail_assigning_document'
        db.add_column(u'assets_unit', 'mail_assigning_document',
                      self.gf('django.db.models.fields.TextField')(default='We have assigned document {{document}} to you'),
                      keep_default=False)

        # Adding field 'Unit.mail_report_fail'
        db.add_column(u'assets_unit', 'mail_report_fail',
                      self.gf('django.db.models.fields.TextField')(default='Your report {{task}} was incorrect.'),
                      keep_default=False)

        # Adding field 'Unit.mail_report_success'
        db.add_column(u'assets_unit', 'mail_report_success',
                      self.gf('django.db.models.fields.TextField')(default='Good work. Report {{task}} was correct.'),
                      keep_default=False)


        # Changing field 'Unit.serial'
        db.alter_column(u'assets_unit', 'serial', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8))
        # Adding unique constraint on 'Unit', fields ['serial']
        db.create_unique(u'assets_unit', ['serial'])


    def backwards(self, orm):
        # Removing unique constraint on 'Unit', fields ['serial']
        db.delete_unique(u'assets_unit', ['serial'])

        # Deleting field 'Unit.tagline'
        db.delete_column(u'assets_unit', 'tagline')

        # Deleting field 'Unit.mail_formal_error_no_subject'
        db.delete_column(u'assets_unit', 'mail_formal_error_no_subject')

        # Deleting field 'Unit.mail_formal_error_missing_form'
        db.delete_column(u'assets_unit', 'mail_formal_error_missing_form')

        # Deleting field 'Unit.mail_formal_error_wrong_unit'
        db.delete_column(u'assets_unit', 'mail_formal_error_wrong_unit')

        # Deleting field 'Unit.mail_formal_error_wrong_form'
        db.delete_column(u'assets_unit', 'mail_formal_error_wrong_form')

        # Deleting field 'Unit.mail_formal_error_redundant_document'
        db.delete_column(u'assets_unit', 'mail_formal_error_redundant_document')

        # Deleting field 'Unit.mail_formal_error_missing_document'
        db.delete_column(u'assets_unit', 'mail_formal_error_missing_document')

        # Deleting field 'Unit.mail_formal_error_wrong_document'
        db.delete_column(u'assets_unit', 'mail_formal_error_wrong_document')

        # Deleting field 'Unit.mail_content_error_unfound_form'
        db.delete_column(u'assets_unit', 'mail_content_error_unfound_form')

        # Deleting field 'Unit.mail_content_error_unfound_task'
        db.delete_column(u'assets_unit', 'mail_content_error_unfound_task')

        # Deleting field 'Unit.mail_content_error_unfound_document'
        db.delete_column(u'assets_unit', 'mail_content_error_unfound_document')

        # Deleting field 'Unit.mail_content_error_existing_form'
        db.delete_column(u'assets_unit', 'mail_content_error_existing_form')

        # Deleting field 'Unit.mail_content_error_existing_task'
        db.delete_column(u'assets_unit', 'mail_content_error_existing_task')

        # Deleting field 'Unit.mail_content_error_existing_document'
        db.delete_column(u'assets_unit', 'mail_content_error_existing_document')

        # Deleting field 'Unit.mail_content_error_unassigned_task'
        db.delete_column(u'assets_unit', 'mail_content_error_unassigned_task')

        # Deleting field 'Unit.mail_assigning_form'
        db.delete_column(u'assets_unit', 'mail_assigning_form')

        # Deleting field 'Unit.mail_assigning_task'
        db.delete_column(u'assets_unit', 'mail_assigning_task')

        # Deleting field 'Unit.mail_assigning_document'
        db.delete_column(u'assets_unit', 'mail_assigning_document')

        # Deleting field 'Unit.mail_report_fail'
        db.delete_column(u'assets_unit', 'mail_report_fail')

        # Deleting field 'Unit.mail_report_success'
        db.delete_column(u'assets_unit', 'mail_report_success')


        # Changing field 'Unit.serial'
        db.alter_column(u'assets_unit', 'serial', self.gf('django.db.models.fields.CharField')(max_length=36))

    models = {
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'isPublished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'5aba6bcc-29db-11e3-a5c5-14109fe17ee1'", 'max_length': '36'})
        },
        u'assets.document': {
            'Meta': {'object_name': 'Document'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'document'", 'unique': 'True', 'null': 'True', 'to': u"orm['provmanager.Provenance']"}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5ab9b7e8-29db-11e3-b17c-14109fe17ee1'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.Task']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            'briefing': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'debriefing': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'isPublished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5ab9d26e-29db-11e3-ae7d-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'5aba03b0-29db-11e3-a004-14109fe17ee1'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {'default': "'Working on Provenance'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdministrative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mail_assigning_document': ('django.db.models.fields.TextField', [], {'default': "'We have assigned document {{document}} to you'"}),
            'mail_assigning_form': ('django.db.models.fields.TextField', [], {'default': "'We have assigned form {{form}} to you.'"}),
            'mail_assigning_task': ('django.db.models.fields.TextField', [], {'default': "'We have assigned task {{task}} to you.'"}),
            'mail_content_error_existing_document': ('django.db.models.fields.TextField', [], {'default': "'You already have access to document {{document}}.'"}),
            'mail_content_error_existing_form': ('django.db.models.fields.TextField', [], {'default': "'You already have access to form {{form}}.'"}),
            'mail_content_error_existing_task': ('django.db.models.fields.TextField', [], {'default': "'You have already been assigned to task {{task}}.'"}),
            'mail_content_error_unassigned_task': ('django.db.models.fields.TextField', [], {'default': "'We could not find task {{task}} your report is about.'"}),
            'mail_content_error_unfound_document': ('django.db.models.fields.TextField', [], {'default': "'Document {{document}} which you requested does not exist within this unit.'"}),
            'mail_content_error_unfound_form': ('django.db.models.fields.TextField', [], {'default': "'Form {{form}} which you requested does not exist.'"}),
            'mail_content_error_unfound_task': ('django.db.models.fields.TextField', [], {'default': "'Task {{task}} which you requested does not exist within this unit.'"}),
            'mail_formal_error_missing_document': ('django.db.models.fields.TextField', [], {'default': "'Your report can only be processed if you attach a document.'"}),
            'mail_formal_error_missing_form': ('django.db.models.fields.TextField', [], {'default': "'You did not attach a form. Please always attach a form.'"}),
            'mail_formal_error_no_subject': ('django.db.models.fields.TextField', [], {'default': "'Your mail cannot be categorized. Please choose a subject next time.'"}),
            'mail_formal_error_redundant_document': ('django.db.models.fields.TextField', [], {'default': "'You have attached an unnecessary document.'"}),
            'mail_formal_error_wrong_document': ('django.db.models.fields.TextField', [], {'default': "'Attached document {{document}} does not belong to report concerning task {{task}}.'"}),
            'mail_formal_error_wrong_form': ('django.db.models.fields.TextField', [], {'default': "'The type of form does not match your request.'"}),
            'mail_formal_error_wrong_unit': ('django.db.models.fields.TextField', [], {'default': "'Form {{form}} cannot be processed by us. Please send it to the appropriate unit.'"}),
            'mail_report_fail': ('django.db.models.fields.TextField', [], {'default': "'Your report {{task}} was incorrect.'"}),
            'mail_report_success': ('django.db.models.fields.TextField', [], {'default': "'Good work. Report {{task}} was correct.'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8'}),
            'tagline': ('django.db.models.fields.CharField', [], {'default': "'Prov is all around you'", 'max_length': '256'})
        },
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 30, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'node2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'5ab9e9f3-29db-11e3-97b3-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['assets']