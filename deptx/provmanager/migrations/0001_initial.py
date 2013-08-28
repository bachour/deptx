# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Provenance'
        db.create_table(u'provmanager_provenance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('store_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'provmanager', ['Provenance'])


    def backwards(self, orm):
        # Deleting model 'Provenance'
        db.delete_table(u'provmanager_provenance')


    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['provmanager']