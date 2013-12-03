# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ProvenanceLog'
        db.delete_table(u'provmanager_provenancelog')


    def backwards(self, orm):
        # Adding model 'ProvenanceLog'
        db.create_table(u'provmanager_provenancelog', (
            ('store_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('counter', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['players.Cron'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal(u'provmanager', ['ProvenanceLog'])


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'attribute1': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'attribute2': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'serial': ('django.db.models.fields.SlugField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['provmanager']