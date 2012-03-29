# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import with_statement

import random
import re
import time
from base64 import urlsafe_b64encode

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File
from django.core.files.storage import DefaultStorage
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.conf import settings
from celery.task import task
from os import mkdir, path, unlink
from errno import EEXIST, ENOENT
from fcntl import flock, LOCK_EX
from zipfile import ZipFile
from traceback import print_exc

from reporting.utils import read_chunks
from celery.task import task
import catalogue.models

# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63


def get_random_hash(seed):
    sha_digest = sha_constructor('%s%s%s%s' %
        (randrange(0, MAX_SESSION_KEY), time.time(), unicode(seed).encode('utf-8', 'replace'),
        settings.SECRET_KEY)).digest()
    return urlsafe_b64encode(sha_digest).replace('=', '').replace('_', '-').lower()


def split_tags(tags):
    result = {}
    for tag in tags:
        result.setdefault(tag.category, []).append(tag)
    return result


class ExistingFile(UploadedFile):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass


class LockFile(object):
    """
    A file lock monitor class; createas an ${objname}.lock
    file in directory dir, and locks it exclusively.
    To be used in 'with' construct.
    """
    def __init__(self, dir, objname):
        self.lockname = path.join(dir, objname + ".lock")

    def __enter__(self):
        self.lock = open(self.lockname, 'w')
        flock(self.lock, LOCK_EX)

    def __exit__(self, *err):
        try:
            unlink(self.lockname)
        except OSError as oe:
            if oe.errno != EEXIST:
                raise oe
        self.lock.close()


@task
def create_zip(paths, zip_slug):
    """
    Creates a zip in MEDIA_ROOT/zip directory containing files from path.
    Resulting archive filename is ${zip_slug}.zip
    Returns it's path relative to MEDIA_ROOT (no initial slash)
    """
    # directory to store zip files
    zip_path = path.join(settings.MEDIA_ROOT, 'zip')

    try:
        mkdir(zip_path)
    except OSError as oe:
        if oe.errno != EEXIST:
            raise oe
    zip_filename = zip_slug + ".zip"

    with LockFile(zip_path, zip_slug):
        if not path.exists(path.join(zip_path, zip_filename)):
            zipf = ZipFile(path.join(zip_path, zip_filename), 'w')
            try:
                for arcname, p in paths:
                    if arcname is None:
                        arcname = path.basename(p)
                    zipf.write(p, arcname)
            finally:
                zipf.close()

        return 'zip/' + zip_filename


def remove_zip(zip_slug):
    """
    removes the ${zip_slug}.zip file from zip store.
    """
    zip_file = path.join(settings.MEDIA_ROOT, 'zip', zip_slug + '.zip')
    try:
        unlink(zip_file)
    except OSError as oe:
        if oe.errno != ENOENT:
            raise oe


class AttachmentHttpResponse(HttpResponse):
    """Response serving a file to be downloaded.
    """
    def __init__ (self, file_path, file_name, mimetype):
        super(AttachmentHttpResponse, self).__init__(mimetype=mimetype)
        self['Content-Disposition'] = 'attachment; filename=%s' % file_name
        self.file_path = file_path
        self.file_name = file_name

        with open(DefaultStorage().path(self.file_path)) as f:
            for chunk in read_chunks(f):
                self.write(chunk)

@task
def async_build_pdf(book_id, customizations, file_name):
    """
    A celery task to generate pdf files.
    Accepts the same args as Book.build_pdf, but with book id as first parameter
    instead of Book instance
    """
    try:
        book = catalogue.models.Book.objects.get(id=book_id)
        print "will gen %s" % DefaultStorage().path(file_name)
        if not DefaultStorage().exists(file_name):
            book.build_pdf(customizations=customizations, file_name=file_name)
        print "done."
    except Exception, e:
        print "Error during pdf creation: %s" % e
        print_exc
        raise e


class MultiQuerySet(object):
    def __init__(self, *args, **kwargs):
        self.querysets = args
        self._count = None
    
    def count(self):
        if not self._count:
            self._count = sum(len(qs) for qs in self.querysets)
        return self._count
    
    def __len__(self):
        return self.count()
        
    def __getitem__(self, item):
        try:
            indices = (offset, stop, step) = item.indices(self.count())
        except AttributeError:
            # it's not a slice - make it one
            return self[item : item + 1][0]
        items = []
        total_len = stop - offset
        for qs in self.querysets:
            if len(qs) < offset:
                offset -= len(qs)
            else:
                items += list(qs[offset:stop])
                if len(items) >= total_len:
                    return items
                else:
                    offset = 0
                    stop = total_len - len(items)
                    continue


def truncate_html_words(s, num, end_text='...'):
    """Truncates HTML to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html. Takes an optional argument of what should be used to notify that the
    string has been truncated, defaulting to ellipsis (...).

    Newlines in the HTML are preserved.

    This is just a version of django.utils.text.truncate_html_words with no space before the end_text.
    """
    s = force_unicode(s)
    length = int(num)
    if length <= 0:
        return u''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    end_text_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or end_text_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i+1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:end_text_pos]
    if end_text:
        out += end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out
