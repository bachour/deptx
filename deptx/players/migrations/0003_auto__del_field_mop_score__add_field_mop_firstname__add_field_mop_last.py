# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Mop.score'
        db.delete_column(u'players_mop', 'score')

        # Adding field 'Mop.firstname'
        db.add_column(u'players_mop', 'firstname',
                      self.gf('django.db.models.fields.CharField')(default='Karl', max_length=100),
                      keep_default=False)

        # Adding field 'Mop.lastname'
        db.add_column(u'players_mop', 'lastname',
                      self.gf('django.db.models.fields.CharField')(default='Klamer', max_length=100),
                      keep_default=False)

        # Adding field 'Mop.dob'
        db.add_column(u'players_mop', 'dob',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 7, 5, 0, 0)),
                      keep_default=False)

        # Adding field 'Mop.gender'
        db.add_column(u'players_mop', 'gender',
                      self.gf('django.db.models.fields.CharField')(default='M', max_length=1),
                      keep_default=False)

        # Adding field 'Mop.weight'
        db.add_column(u'players_mop', 'weight',
                      self.gf('django.db.models.fields.IntegerField')(default=100),
                      keep_default=False)

        # Adding field 'Mop.height'
        db.add_column(u'players_mop', 'height',
                      self.gf('django.db.models.fields.IntegerField')(default=180),
                      keep_default=False)

        # Adding field 'Mop.marital'
        db.add_column(u'players_mop', 'marital',
                      self.gf('django.db.models.fields.CharField')(default='S', max_length=1),
                      keep_default=False)

        # Adding field 'Mop.hair'
        db.add_column(u'players_mop', 'hair',
                      self.gf('django.db.models.fields.CharField')(default='BLO', max_length=3),
                      keep_default=False)

        # Adding field 'Mop.eyes'
        db.add_column(u'players_mop', 'eyes',
                      self.gf('django.db.models.fields.CharField')(default='BLU', max_length=3),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Mop.score'
        db.add_column(u'players_mop', 'score',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'Mop.firstname'
        db.delete_column(u'players_mop', 'firstname')

        # Deleting field 'Mop.lastname'
        db.delete_column(u'players_mop', 'lastname')

        # Deleting field 'Mop.dob'
        db.delete_column(u'players_mop', 'dob')

        # Deleting field 'Mop.gender'
        db.delete_column(u'players_mop', 'gender')

        # Deleting field 'Mop.weight'
        db.delete_column(u'players_mop', 'weight')

        # Deleting field 'Mop.height'
        db.delete_column(u'players_mop', 'height')

        # Deleting field 'Mop.marital'
        db.delete_column(u'players_mop', 'marital')

        # Deleting field 'Mop.hair'
        db.delete_column(u'players_mop', 'hair')

        # Deleting field 'Mop.eyes'
        db.delete_column(u'players_mop', 'eyes')


    models = {
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
        u'players.cron': {
            'Meta': {'object_name': 'Cron'},
            'episode': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['players.Player']", 'unique': 'True'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'players.mop': {
            'Meta': {'object_name': 'Mop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {}),
            'eyes': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'hair': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'marital': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.Player']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
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

    complete_apps = ['players']