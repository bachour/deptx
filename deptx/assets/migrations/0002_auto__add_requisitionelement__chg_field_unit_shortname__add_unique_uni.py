# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RequisitionElement'
        db.create_table(u'assets_requisitionelement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Unit'])),
        ))
        db.send_create_signal(u'assets', ['RequisitionElement'])


        # Changing field 'Unit.shortname'
        db.alter_column(u'assets_unit', 'shortname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16))
        # Adding unique constraint on 'Unit', fields ['shortname']
        db.create_unique(u'assets_unit', ['shortname'])


    def backwards(self, orm):
        # Removing unique constraint on 'Unit', fields ['shortname']
        db.delete_unique(u'assets_unit', ['shortname'])

        # Deleting model 'RequisitionElement'
        db.delete_table(u'assets_requisitionelement')


        # Changing field 'Unit.shortname'
        db.alter_column(u'assets_unit', 'shortname', self.gf('django.db.models.fields.CharField')(max_length=10))

    models = {
        u'assets.requisitionelement': {
            'Meta': {'object_name': 'RequisitionElement'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Unit']"})
        },
        u'assets.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shortname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        }
    }

    complete_apps = ['assets']