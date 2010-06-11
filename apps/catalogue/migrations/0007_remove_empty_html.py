# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
    def forwards(self, orm):
        """ Look for HTML files without any real content and delete them """
        from lxml import etree
        from librarian import html_has_content
        
        for book in orm.Book.objects.exclude(html_file=''):
            if not html_has_content(etree.parse(book.html_file)):
                book.html_file.delete()
                # must do it by hand, we don't see real Book.save
                for key in filter(lambda x: x.startswith('_short_html'), book.__dict__):
                    book.__setattr__(key, '')
                book.save()
    
    def backwards(self, orm):
        """ Do nothing. We don't want empty HTML files anyway. """
        pass
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'catalogue.book': {
            'Meta': {'object_name': 'Book'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            '_short_html_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_tag_counter': ('catalogue.fields.JSONField', [], {'default': "''"}),
            '_theme_counter': ('catalogue.fields.JSONField', [], {'default': "''"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'epub_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'extra_info': ('catalogue.fields.JSONField', [], {}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mp3_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'odt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'ogg_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'txt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalogue.bookstub': {
            'Meta': {'object_name': 'BookStub'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'translator': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'translator_death': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'catalogue.fragment': {
            'Meta': {'object_name': 'Fragment'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            '_short_html_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fragments'", 'to': "orm['catalogue.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_text': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'catalogue.tag': {
            'Meta': {'object_name': 'Tag'},
            'book_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'death': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'sort_key': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'})
        },
        'catalogue.tagrelation': {
            'Meta': {'unique_together': "(('tag', 'content_type', 'object_id'),)", 'object_name': 'TagRelation', 'db_table': "'catalogue_tag_relation'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['catalogue.Tag']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['catalogue']
