# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'DocumentInstance'
        db.delete_table(u'mop_documentinstance')

        # Adding model 'MopDocumentInstance'
        db.create_table(u'mop_mopdocumentinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('mop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Mop'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('modified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('used', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('provenanceState', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('randomizedDocument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.RandomizedDocument'], null=True, blank=True)),
            ('cronDocument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.CronDocument'], null=True, blank=True)),
        ))
        db.send_create_signal(u'mop', ['MopDocumentInstance'])

        # Deleting field 'Mail.documentInstance'
        db.delete_column(u'mop_mail', 'documentInstance_id')

        # Adding field 'Mail.mopDocumentInstance'
        db.add_column(u'mop_mail', 'mopDocumentInstance',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.MopDocumentInstance'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'DocumentInstance'
        db.create_table(u'mop_documentinstance', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('used', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Mop'])),
            ('cronDocument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.CronDocument'], null=True, blank=True)),
            ('randomizedDocument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.RandomizedDocument'], null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('provenanceState', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'mop', ['DocumentInstance'])

        # Deleting model 'MopDocumentInstance'
        db.delete_table(u'mop_mopdocumentinstance')

        # Adding field 'Mail.documentInstance'
        db.add_column(u'mop_mail', 'documentInstance',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.DocumentInstance'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Mail.mopDocumentInstance'
        db.delete_column(u'mop_mail', 'mopDocumentInstance_id')


    models = {
        u'assets.abstractdocument': {
            'Meta': {'object_name': 'AbstractDocument'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'document'", 'unique': 'True', 'to': u"orm['provmanager.Provenance']"}),
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
            'serial': ('django.db.models.fields.SlugField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assets.crondocument': {
            'Meta': {'object_name': 'CronDocument', '_ormbases': [u'assets.AbstractDocument']},
            u'abstractdocument_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.AbstractDocument']", 'unique': 'True', 'primary_key': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']"}),
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
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '16', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
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
            'tagline': ('django.db.models.fields.CharField', [], {'default': "'Prov is all around you'", 'max_length': '256'})
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
        u'mop.badge': {
            'Meta': {'object_name': 'Badge'},
            'badge': ('django.db.models.fields.IntegerField', [], {}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"})
        },
        u'mop.mail': {
            'Meta': {'object_name': 'Mail'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'mopDocumentInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.MopDocumentInstance']", 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requisitionInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionInstance']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
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
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'mop.randomizeddocument': {
            'Meta': {'object_name': 'RandomizedDocument'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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
            'data': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'players.mop': {
            'Meta': {'object_name': 'Mop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'clearance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Player']"}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'1ba2f1e8-4bbc-11e3-9c20'", 'max_length': '36'}),
            'totalTrust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['mop']