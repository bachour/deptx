# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Provenance.store_id'
        db.alter_column(u'provmanager_provenance', 'store_id', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Provenance.store_id'
        raise RuntimeError("Cannot reverse this migration. 'Provenance.store_id' and its values cannot be restored.")

    models = {
        u'provmanager.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'graphml': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'serial': ('django.db.models.fields.SlugField', [], {'default': "'0b4c3d51-1bb6-11e3-8b51-14109fe17ee1'", 'max_length': '36'}),
            'store_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['provmanager']