# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'MopProvenanceInstance'
        db.delete_table(u'provmanager_mopprovenanceinstance')

        # Deleting model 'CronProvenanceInstance'
        db.delete_table(u'provmanager_cronprovenanceinstance')


    def backwards(self, orm):
        # Adding model 'MopProvenanceInstance'
        db.create_table(u'provmanager_mopprovenanceinstance', (
            ('mop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Mop'])),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['provmanager.Provenance'])),
            ('submitted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currentState', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'provmanager', ['MopProvenanceInstance'])

        # Adding model 'CronProvenanceInstance'
        db.create_table(u'provmanager_cronprovenanceinstance', (
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['provmanager.Provenance'])),
            ('submitted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Cron'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currentState', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'provmanager', ['CronProvenanceInstance'])


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'node2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'e81ed58a-1c83-11e3-9703-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['provmanager']