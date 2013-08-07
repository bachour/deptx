# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Player'
        db.delete_table(u'cron_player')

        # Adding model 'CaseInstance'
        db.create_table(u'cron_caseinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Case'])),
            ('crontracker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cron.CronTracker'])),
            ('progress', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'cron', ['CaseInstance'])


    def backwards(self, orm):
        # Adding model 'Player'
        db.create_table(u'cron_player', (
            ('firstName', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('lastName', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=256)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'cron', ['Player'])

        # Deleting model 'CaseInstance'
        db.delete_table(u'cron_caseinstance')


    models = {
        u'assets.case': {
            'Meta': {'object_name': 'Case'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'25771102-f9f9-11e2-805f-14109fe17ee1'", 'max_length': '36'})
        },
        u'assets.mission': {
            'Meta': {'object_name': 'Mission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
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
        u'cron.caseinstance': {
            'Meta': {'object_name': 'CaseInstance'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Case']"}),
            'crontracker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cron.CronTracker']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'progress': ('django.db.models.fields.IntegerField', [], {})
        },
        u'cron.crontracker': {
            'Meta': {'object_name': 'CronTracker'},
            'cron': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['players.Cron']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Mission']"}),
            'progress': ('django.db.models.fields.IntegerField', [], {})
        },
        u'players.cron': {
            'Meta': {'object_name': 'Cron'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['players.Player']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'players.player': {
            'Meta': {'object_name': 'Player'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['cron']