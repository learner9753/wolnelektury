# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _

from catalogue.models import Book, Tag


class Deleted(models.Model):
    object_id = models.IntegerField()
    slug = models.SlugField(_('slug'), max_length=120, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType)
    category = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(editable=False, db_index=True)
    deleted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (('content_type', 'object_id'),)


def _pre_delete_handler(sender, instance, **kwargs):
    """ save deleted objects for change history purposes """

    if sender in (Book, Tag):
        if sender == Tag:
            if instance.category in ('book', 'set'):
                return
            else:
                category = instance.category
        else:
            category = None
        content_type = ContentType.objects.get_for_model(sender)
        Deleted.objects.create(
            content_type=content_type, object_id=instance.id, created_at=instance.created_at, category=category,
            slug=instance.slug)
pre_delete.connect(_pre_delete_handler)
