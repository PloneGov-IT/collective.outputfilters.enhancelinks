# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.outputfilters.enhancelinks.interfaces import ILinkEnhancerProvider  # noqa
from collective.outputfilters.enhancelinks.tests.base import BaseTest
from collective.outputfilters.enhancelinks.testing import COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

FILE_ICON_URLS = [
    'http://nohost/plone/pdf.png',
    'http://nohost/plone/++resource++mimetype.icons/pdf.png'
]

IMAGE_ICON_URLS = [
    'http://nohost/plone/image.png',
    'http://nohost/plone/++resource++mimetype.icons/image.png'
]

FILE_DOWNLOAD_URLS = [
    '/at_download/file/file.pdf',
    '/@@download/file/file.pdf'
]


class TestAdapter(BaseTest):
    """
    Test that collective.outputfilters.enhancelinks is properly installed.
    """

    layer = COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.file = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        self.image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            image=self.get_attachment(u'image.jpg', type='image'))
        self.document = api.content.create(
            type='Document',
            title='A page',
            container=self.portal)
        self.file_provider = ILinkEnhancerProvider(self.file, None)
        self.img_provider = ILinkEnhancerProvider(self.image, None)

    def test_adapter_guess_mimetype(self):
        """Test if the method find the correct mimetype"""
        # I pass False because it isn't a DX content
        file_item = self.get_right_file(item=self.file, type='file')
        image_item = self.get_right_file(item=self.image, type='image')
        mimetype = self.extract_mimetype(file_item)
        self.assertEqual(len(mimetype), 1)
        self.assertEqual(mimetype[0].id, 'PDF document')
        img_mimetype = self.extract_mimetype(image_item)
        self.assertEqual(len(img_mimetype), 1)
        self.assertEqual(img_mimetype[0].id, 'JPEG image')

    def test_adapter_format_obj_size(self):
        """Test if the method returns a correct obj size"""
        self.assertEqual(
            self.file_provider.get_formatted_size(self.file.file),
            '8.4 KB')
        self.assertEqual(
            self.img_provider.get_formatted_size(self.image.image),
            '5.0 KB')

    def test_adapter_extract_infos_from_mime(self):
        """ Test if the method returns the correct infos """
        file_item = self.get_right_file(item=self.file, type='file')
        image_item = self.get_right_file(item=self.image, type='image')
        mimetype = self.extract_mimetype(file_item)
        infos = self.file_provider.extract_infos(
            file_item,
            mimetype)
        self.assertIn(infos.get('icon_url'), FILE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.4 KB')
        self.assertIn(infos.get('url_suffix'), FILE_DOWNLOAD_URLS)

        img_mimetype = self.extract_mimetype(image_item)
        infos = self.img_provider.extract_infos(
            image_item,
            img_mimetype)
        self.assertIn(infos.get('icon_url'), IMAGE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.0 KB')
        self.assertEqual(infos.get('url_suffix'), '')

    def test_adapter_for_file(self):
        """Test if the view returns the correct infos for a file"""
        infos = self.file_provider.get_link_details()
        self.assertIn(infos.get('icon_url'), FILE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.4 KB')
        self.assertIn(infos.get('url_suffix'), FILE_DOWNLOAD_URLS)

    def test_adapter_for_image(self):
        """Test if the view returns the correct infos for an image"""
        infos = self.img_provider.get_link_details()
        self.assertIn(infos.get('icon_url'), IMAGE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.0 KB')
        self.assertEqual(infos.get('url_suffix'), '')
