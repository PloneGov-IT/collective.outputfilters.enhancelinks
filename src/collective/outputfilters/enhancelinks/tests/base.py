# -*- coding: utf-8 -*-
from plone import api
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage

import os
import unittest2 as unittest


class BaseTest(unittest.TestCase):
    def get_right_file(self, item, type):
        if api.env.plone_version() < '5.0':
            # AT
            return item.getFile()
        if type == 'image':
            return item.image
        return item.file

    def extract_mimetype(self, file_item):
        content_type = (
            api.env.plone_version() < '5.0'
            and file_item.getContentType()
            or file_item.contentType
        )
        return self.file_provider.guess_mimetype(
            content_type, file_item.filename
        )

    def get_attachment(self, filename, type):
        file_path = os.path.join(os.path.dirname(__file__), filename)
        with open(file_path, 'rb') as f:
            if api.env.plone_version() < '5.0':
                return f
            if type == 'image':
                return NamedImage(data=f, filename=filename)
            return NamedFile(data=f, filename=filename)

    def file_icon_compare_str(self):
        icon_url = ''
        if api.env.plone_version() < '5.1':
            icon_url = 'http://nohost/plone/pdf.png'
        else:
            icon_url = 'http://nohost/plone/++resource++mimetype.icons/pdf.png'
        return '<img src="{0}" class="attachmentLinkIcon"'.format(icon_url)

    def image_icon_compare_str(self):
        icon_url = ''
        if api.env.plone_version() < '5.1':
            icon_url = 'http://nohost/plone/image.png'
        else:
            icon_url = (
                'http://nohost/plone/++resource++mimetype.icons/image.png'
            )
        return '<img src="{0}" class="attachmentLinkIcon"'.format(icon_url)
