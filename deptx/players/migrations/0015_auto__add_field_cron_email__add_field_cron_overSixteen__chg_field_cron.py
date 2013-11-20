# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Cron.email'
        db.add_column(u'players_cron', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='hello@bello.cello', max_length=75),
                      keep_default=False)

        # Adding field 'Cron.overSixteen'
        db.add_column(u'players_cron', 'overSixteen',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Cron.player'
        db.alter_column(u'players_cron', 'player_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['players.Player'], unique=True, null=True))
        # Deleting field 'Player.firstName'
        db.delete_column(u'players_player', 'firstName')

        # Deleting field 'Player.lastName'
        db.delete_column(u'players_player', 'lastName')

        # Deleting field 'Player.email'
        db.delete_column(u'players_player', 'email')

        # Adding field 'Player.name'
        db.add_column(u'players_player', 'name',
                      self.gf('django.db.models.fields.CharField')(default='sandy', max_length=128),
                      keep_default=False)

        # Adding field 'Player.gender'
        db.add_column(u'players_player', 'gender',
                      self.gf('django.db.models.fields.IntegerField')(default=2),
                      keep_default=False)

        # Adding field 'Player.age'
        db.add_column(u'players_player', 'age',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Player.town'
        db.add_column(u'players_player', 'town',
                      self.gf('django.db.models.fields.CharField')(default='entenhausen', max_length=128),
                      keep_default=False)

        # Adding field 'Player.country'
        db.add_column(u'players_player', 'country',
                      self.gf('django.db.models.fields.CharField')(default='latveria', max_length=128),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Cron.email'
        db.delete_column(u'players_cron', 'email')

        # Deleting field 'Cron.overSixteen'
        db.delete_column(u'players_cron', 'overSixteen')


        # User chose to not deal with backwards NULL issues for 'Cron.player'
        raise RuntimeError("Cannot reverse this migration. 'Cron.player' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Player.firstName'
        raise RuntimeError("Cannot reverse this migration. 'Player.firstName' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Player.lastName'
        raise RuntimeError("Cannot reverse this migration. 'Player.lastName' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Player.email'
        raise RuntimeError("Cannot reverse this migration. 'Player.email' and its values cannot be restored.")
        # Deleting field 'Player.name'
        db.delete_column(u'players_player', 'name')

        # Deleting field 'Player.gender'
        db.delete_column(u'players_player', 'gender')

        # Deleting field 'Player.age'
        db.delete_column(u'players_player', 'age')

        # Deleting field 'Player.town'
        db.delete_column(u'players_player', 'town')

        # Deleting field 'Player.country'
        db.delete_column(u'players_player', 'country')


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
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'activationCode': ('django.db.models.fields.CharField', [], {'default': "'f8cbbccf-51ef-11e3-ad5b'", 'max_length': '36'}),
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
            'serial': ('django.db.models.fields.CharField', [], {'default': "'f8cbf36b-51ef-11e3-a280'", 'max_length': '36'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
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
        }
    }

    complete_apps = ['players']