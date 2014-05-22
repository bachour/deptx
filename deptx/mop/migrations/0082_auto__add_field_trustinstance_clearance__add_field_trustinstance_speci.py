# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TrustInstance.clearance'
        db.add_column(u'mop_trustinstance', 'clearance',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'TrustInstance.specialStatus'
        db.add_column(u'mop_trustinstance', 'specialStatus',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TrustInstance.clearance'
        db.delete_column(u'mop_trustinstance', 'clearance')

        # Deleting field 'TrustInstance.specialStatus'
        db.delete_column(u'mop_trustinstance', 'specialStatus')


    models = {
        u'assets.abstractdocument': {
            'Meta': {'object_name': 'AbstractDocument'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'guide': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'document'", 'unique': 'True', 'null': 'True', 'to': u"orm['provmanager.Provenance']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'isPublished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'preCase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']", 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'report': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assets.crondocument': {
            'Meta': {'object_name': 'CronDocument', '_ormbases': [u'assets.AbstractDocument']},
            u'abstractdocument_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.AbstractDocument']", 'unique': 'True', 'primary_key': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'crondocument'", 'to': u"orm['assets.Case']"}),
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            'activity': ('django.db.models.fields.TextField', [], {'default': "'ENTER ACTIVITY TEXT FOR MISSION'"}),
            'briefing': ('django.db.models.fields.TextField', [], {'default': "'ENTER BRIEFING FOR MISSION'"}),
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'debriefing': ('django.db.models.fields.TextField', [], {'default': "'ENTER DEBRIEFING FOR MISSION'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'default': "'ENTER INTRO FOR MISSION'"}),
            'isPublished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'default': "'ENTER OUTRO FOR MISSION'"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assets.mopdocument': {
            'Meta': {'object_name': 'MopDocument', '_ormbases': [u'assets.AbstractDocument']},
            u'abstractdocument_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.AbstractDocument']", 'unique': 'True', 'primary_key': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.storyfile': {
            'Meta': {'object_name': 'StoryFile'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediatype': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'serial': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '36'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "'Working on Provenance'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_assigning_document': ('django.db.models.fields.TextField', [], {'default': "'We have assigned document {{data}} to you'"}),
            'mail_assigning_form': ('django.db.models.fields.TextField', [], {'default': "'We have assigned form {{data}} to you.'"}),
            'mail_error_existing_document': ('django.db.models.fields.TextField', [], {'default': "'You already have access to document {{data}}.'"}),
            'mail_error_existing_form': ('django.db.models.fields.TextField', [], {'default': "'You already have access to form {{data}}.'"}),
            'mail_error_lacking_trust': ('django.db.models.fields.TextField', [], {'default': "'You do not have the required amount of performance credits to request document {{data}}.'"}),
            'mail_error_missing_document': ('django.db.models.fields.TextField', [], {'default': "'Your report can only be processed if you attach a document.'"}),
            'mail_error_missing_form': ('django.db.models.fields.TextField', [], {'default': "'You did not attach a form. Please always attach a form.'"}),
            'mail_error_no_subject': ('django.db.models.fields.TextField', [], {'default': "'Your mail could not be filtered automatically. Please choose an appropriate subject next time.'"}),
            'mail_error_redundant_document': ('django.db.models.fields.TextField', [], {'default': "'You have attached an unnecessary document.'"}),
            'mail_error_unfound_document': ('django.db.models.fields.TextField', [], {'default': "'Document {{data}} which you requested does not exist.'"}),
            'mail_error_unfound_form': ('django.db.models.fields.TextField', [], {'default': "'Form {{data}} which you requested does not exist.'"}),
            'mail_error_wrong_document': ('django.db.models.fields.TextField', [], {'default': "'Attached document {{data}} does not match the report.'"}),
            'mail_error_wrong_form': ('django.db.models.fields.TextField', [], {'default': "'The type of form does not match your request.'"}),
            'mail_error_wrong_unit': ('django.db.models.fields.TextField', [], {'default': "'Form {{data}} cannot be processed by us. Please send it to the appropriate unit.'"}),
            'mail_report_fail': ('django.db.models.fields.TextField', [], {'default': "'Your report {{data}} was incorrect.'"}),
            'mail_report_success': ('django.db.models.fields.TextField', [], {'default': "'Good work. Report {{data}} was correct.'"}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8'}),
            'tagline': ('django.db.models.fields.CharField', [], {'default': "'Prov is all around you'", 'max_length': '256'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mop.mail': {
            'Meta': {'object_name': 'Mail'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'bodyType': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'mopDocumentInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.MopDocumentInstance']", 'null': 'True', 'blank': 'True'}),
            'needsReply': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performanceInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.PerformanceInstance']", 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'replyTo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.Mail']", 'null': 'True', 'blank': 'True'}),
            'requisitionBlank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionBlank']", 'null': 'True', 'blank': 'True'}),
            'requisitionInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionInstance']", 'null': 'True', 'blank': 'True'}),
            'sentAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 20, 0, 0)'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']", 'null': 'True', 'blank': 'True'})
        },
        u'mop.mopdocumentinstance': {
            'Meta': {'object_name': 'MopDocumentInstance'},
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'cronDocument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.CronDocument']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'provenanceState': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'randomizedDocument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RandomizedDocument']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'mop.mopfile': {
            'Meta': {'object_name': 'MopFile'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"})
        },
        u'mop.moptracker': {
            'Meta': {'object_name': 'MopTracker'},
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fileUploadAllowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hasCheckedInbox': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mopTracker'", 'unique': 'True', 'to': u"orm['players.Mop']"}),
            'specialStatusAllowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'totalTrust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tutorial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tutorialProvErrors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unreadEmails': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'mop.performanceinstance': {
            'Meta': {'object_name': 'PerformanceInstance'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'performance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.PerformancePeriod']"}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '3'})
        },
        u'mop.performanceperiod': {
            'Meta': {'object_name': 'PerformancePeriod'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reviewDate': ('django.db.models.fields.DateField', [], {}),
            'reviewTime': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'mop.randomizeddocument': {
            'Meta': {'object_name': 'RandomizedDocument'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isTutorial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']", 'null': 'True', 'blank': 'True'}),
            'mopDocument': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.MopDocument']"}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'randomizedDocument'", 'unique': 'True', 'to': u"orm['provmanager.Provenance']"}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'mop.requisitionblank': {
            'Meta': {'object_name': 'RequisitionBlank'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'requisition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Requisition']"})
        },
        u'mop.requisitioninstance': {
            'Meta': {'object_name': 'RequisitionInstance'},
            'blank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionBlank']"}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'mop.storyfileinstance': {
            'Meta': {'object_name': 'StoryFileInstance'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'storyFile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.StoryFile']"})
        },
        u'mop.trustinstance': {
            'Meta': {'object_name': 'TrustInstance'},
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'newTrust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'oldTrust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'specialStatus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'totalTrust': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'players.cron': {
            'Meta': {'object_name': 'Cron'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'activationCode': ('django.db.models.fields.CharField', [], {'default': "'717bbe99-e053-11e3-a57f'", 'max_length': '36'}),
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'overSixteen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['players.Player']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'players.mop': {
            'Meta': {'object_name': 'Mop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'cron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Cron']"}),
            'dob': ('django.db.models.fields.DateField', [], {}),
            'eyes': ('django.db.models.fields.IntegerField', [], {}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            'hair': ('django.db.models.fields.IntegerField', [], {}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'marital': ('django.db.models.fields.IntegerField', [], {}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mop'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'age': ('django.db.models.fields.IntegerField', [], {}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
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

    complete_apps = ['mop']