# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TrustTracker'
        db.delete_table(u'mop_trusttracker')

        # Adding model 'TrustInstance'
        db.create_table(u'mop_trustinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Mop'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 8, 0, 0), auto_now=True, blank=True)),
            ('taskInstance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.TaskInstance'], null=True, blank=True)),
            ('documentInstance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.DocumentInstance'], null=True, blank=True)),
            ('weekModifier', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'mop', ['TrustInstance'])


    def backwards(self, orm):
        # Adding model 'TrustTracker'
        db.create_table(u'mop_trusttracker', (
            ('documentInstance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.DocumentInstance'], null=True, blank=True)),
            ('taskInstance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mop.TaskInstance'], null=True, blank=True)),
            ('mop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Mop'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 8, 0, 0), auto_now=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'mop', ['TrustTracker'])

        # Deleting model 'TrustInstance'
        db.delete_table(u'mop_trustinstance')


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
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'660104de-3069-11e3-a016'", 'max_length': '36'})
        },
        u'assets.document': {
            'Meta': {'object_name': 'Document'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'provenance': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'document'", 'unique': 'True', 'null': 'True', 'to': u"orm['provmanager.Provenance']"}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'66012361-3069-11e3-879f'", 'max_length': '36'}),
            'task': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['assets.Task']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            'activity': ('django.db.models.fields.TextField', [], {'default': "'ENTER ACTIVITY TEXT FOR MISSION'"}),
            'briefing': ('django.db.models.fields.TextField', [], {'default': "'ENTER BRIEFING FOR MISSION'"}),
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'debriefing': ('django.db.models.fields.TextField', [], {'default': "'ENTER DEBRIEFING FOR MISSION'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'default': "'ENTER INTRO FOR MISSION'"}),
            'isPublished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'outro': ('django.db.models.fields.TextField', [], {'default': "'ENTER OUTRO FOR MISSION'"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'65e38fb3-3069-11e3-893c'", 'max_length': '50'})
        },
        u'assets.requisition': {
            'Meta': {'object_name': 'Requisition'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInitial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'66018882-3069-11e3-8a50'", 'max_length': '36'}),
            'trust': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.task': {
            'Meta': {'object_name': 'Task'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'6602a397-3069-11e3-9d50'", 'max_length': '36'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {'default': "'Working on Provenance'"}),
            'handsOutDocuments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'handsOutForms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_assigning_document': ('django.db.models.fields.TextField', [], {'default': "'We have assigned document {{data}} to you'"}),
            'mail_assigning_form': ('django.db.models.fields.TextField', [], {'default': "'We have assigned form {{data}} to you.'"}),
            'mail_assigning_task': ('django.db.models.fields.TextField', [], {'default': "'We have assigned task {{data}} to you.'"}),
            'mail_error_existing_document': ('django.db.models.fields.TextField', [], {'default': "'You already have access to document {{data}}.'"}),
            'mail_error_existing_form': ('django.db.models.fields.TextField', [], {'default': "'You already have access to form {{data}}.'"}),
            'mail_error_existing_task': ('django.db.models.fields.TextField', [], {'default': "'You have already been assigned to task {{data}}.'"}),
            'mail_error_missing_document': ('django.db.models.fields.TextField', [], {'default': "'Your report can only be processed if you attach a document.'"}),
            'mail_error_missing_form': ('django.db.models.fields.TextField', [], {'default': "'You did not attach a form. Please always attach a form.'"}),
            'mail_error_no_subject': ('django.db.models.fields.TextField', [], {'default': "'Your mail could not be filtered automatically. Please choose an appropriate subject next time.'"}),
            'mail_error_redundant_document': ('django.db.models.fields.TextField', [], {'default': "'You have attached an unnecessary document.'"}),
            'mail_error_unassigned_task': ('django.db.models.fields.TextField', [], {'default': "'We could not find task {{data}} your report is about.'"}),
            'mail_error_unfound_document': ('django.db.models.fields.TextField', [], {'default': "'Document {{data}} which you requested does not exist.'"}),
            'mail_error_unfound_form': ('django.db.models.fields.TextField', [], {'default': "'Form {{data}} which you requested does not exist.'"}),
            'mail_error_unfound_task': ('django.db.models.fields.TextField', [], {'default': "'Task {{data}} which you requested does not exist within this unit.'"}),
            'mail_error_wrong_document': ('django.db.models.fields.TextField', [], {'default': "'Attached document {{data}} does not belong to report concerning task {{task}}.'"}),
            'mail_error_wrong_form': ('django.db.models.fields.TextField', [], {'default': "'The type of form does not match your request.'"}),
            'mail_error_wrong_unit': ('django.db.models.fields.TextField', [], {'default': "'Form {{data}} cannot be processed by us. Please send it to the appropriate unit.'"}),
            'mail_report_fail': ('django.db.models.fields.TextField', [], {'default': "'Your report {{data}} was incorrect.'"}),
            'mail_report_success': ('django.db.models.fields.TextField', [], {'default': "'Good work. Report {{data}} was correct.'"}),
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
        u'mop.documentinstance': {
            'Meta': {'object_name': 'DocumentInstance'},
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'provenanceState': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'mop.mail': {
            'Meta': {'object_name': 'Mail'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'documentInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.DocumentInstance']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requisitionInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionInstance']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']", 'null': 'True', 'blank': 'True'})
        },
        u'mop.requisitionblank': {
            'Meta': {'object_name': 'RequisitionBlank'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'requisition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Requisition']"})
        },
        u'mop.requisitioninstance': {
            'Meta': {'object_name': 'RequisitionInstance'},
            'blank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.RequisitionBlank']"}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'mop.taskinstance': {
            'Meta': {'object_name': 'TaskInstance'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Task']"})
        },
        u'mop.trustinstance': {
            'Meta': {'object_name': 'TrustInstance'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'documentInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.DocumentInstance']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Mop']"}),
            'taskInstance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mop.TaskInstance']", 'null': 'True', 'blank': 'True'}),
            'weekModifier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'players.mop': {
            'Meta': {'object_name': 'Mop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {}),
            'eyes': ('django.db.models.fields.IntegerField', [], {}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            'hair': ('django.db.models.fields.IntegerField', [], {}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'marital': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Player']"}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'66030085-3069-11e3-88f4'", 'max_length': '36'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 8, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'node2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'6601a0c2-3069-11e3-bdad'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['mop']