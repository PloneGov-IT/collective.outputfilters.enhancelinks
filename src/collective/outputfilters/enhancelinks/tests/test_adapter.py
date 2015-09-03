# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.outputfilters.enhancelinks.interfaces import ILinkEnhancerProvider  # noqa
from collective.outputfilters.enhancelinks.testing import COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
import os
import unittest2 as unittest


class TestAdapter(unittest.TestCase):
    """
    Test that collective.outputfilters.enhancelinks is properly installed.
    """

    layer = COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        file_path = os.path.join(os.path.dirname(__file__), "file.pdf")
        image_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        self.file = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=open(file_path))
        self.image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            image=open(image_path))
        self.document = api.content.create(
            type='Document',
            title='A page',
            container=self.portal)
        self.file_provider = ILinkEnhancerProvider(self.file, None)
        self.img_provider = ILinkEnhancerProvider(self.image, None)

    def test_adapter_guess_mimetype(self):
        """Test if the method find the correct mimetype"""
        # I pass False because it isn't a DX content
        mimetype = self.file_provider.guess_mimetype(
            self.file.getFile().getContentType(),
            self.file.getFile().filename)
        self.assertEqual(len(mimetype), 1)
        self.assertEqual(mimetype[0].id, 'PDF document')
        img_mimetype = self.img_provider.guess_mimetype(
            self.image.getFile().getContentType(),
            self.image.getFile().filename)
        self.assertEqual(len(img_mimetype), 1)
        self.assertEqual(img_mimetype[0].id, 'JPEG image')

    def test_adapter_format_obj_size(self):
        """Test if the method returns a correct obj size"""
        self.assertEqual(
            self.file_provider.get_formatted_size(self.file.getFile()),
            '8.4 KB')
        self.assertEqual(
            self.img_provider.get_formatted_size(self.image.getFile()),
            '5.0 KB')

    def test_adapter_extract_infos_from_mime(self):
        """ Test if the method returns the correct infos """
        mimetype = self.file_provider.guess_mimetype(
            self.file.getFile().getContentType(),
            self.file.getFile().filename)
        infos = self.file_provider.extract_infos(
            self.file.getFile(),
            mimetype)
        self.assertEqual(infos.get('icon_url'), 'http://nohost/plone/pdf.png')
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.4 KB')
        self.assertEqual(infos.get('url_suffix'), '/at_download/file/file.pdf')

        mimetype = self.img_provider.guess_mimetype(
            self.image.getFile().getContentType(),
            self.image.getFile().filename)
        infos = self.img_provider.extract_infos(
            self.image.getFile(),
            mimetype)
        self.assertEqual(infos.get('icon_url'), 'http://nohost/plone/image.png')
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.0 KB')
        self.assertEqual(infos.get('url_suffix'), '')

    def test_adapter_for_file(self):
        """Test if the view returns the correct infos for a file"""
        infos = self.file_provider.get_link_details()
        self.assertEqual(infos.get('icon_url'), 'http://nohost/plone/pdf.png')
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.4 KB')
        self.assertEqual(infos.get('url_suffix'), '/at_download/file/file.pdf')

    def test_adapter_for_image(self):
        """Test if the view returns the correct infos for an image"""
        infos = self.img_provider.get_link_details()
        self.assertEqual(infos.get('icon_url'), 'http://nohost/plone/image.png')
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.0 KB')
        self.assertEqual(infos.get('url_suffix'), '')
