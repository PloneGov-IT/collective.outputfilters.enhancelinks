# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.outputfilters.enhancelinks.enhance_links import EnhanceLinks
from collective.outputfilters.enhancelinks.testing import COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
import os
import unittest2 as unittest


class TestFilter(unittest.TestCase):
    """Test that the outputfilter works correctly"""

    layer = COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.output_filter = EnhanceLinks()

    def test_filter_does_nothing(self):
        """Test if the filter does nothing without hrefs in html"""
        html = """
            <p>This is a simple <strong>formatted text</strong>.</p>
            <p>Nothing else.</p>"""
        self.assertEqual(self.output_filter(html), html)

    def test_filter_with_external_link(self):
        """Test if the filter does nothing without hrefs in html"""
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an <a class="external-link" href="https://plone.org" ' \
            'target="_self" title=""> external link</a></p>'
        self.assertEqual(self.output_filter(html), html)

    def test_filter_with_link_to_document(self):
        """Test if the filter does nothing without hrefs in html"""
        document = api.content.create(
            type='Document',
            title='A page',
            container=self.portal)
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/%s" target="_self" ' \
            'title="">internal link</a></p>' % document.UID()
        self.assertEqual(self.output_filter(html), html)

    def test_filter_with_link_to_file(self):
        """Test if the filter works properly with a link to a file"""
        file_path = os.path.join(os.path.dirname(__file__), "file.pdf")
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=open(file_path))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/%s" target="_self" ' \
            'title="">internal link</a></p>' % file_obj.UID()
        new_html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an <a class="internal-link" ' \
            'href="resolveuid/%s/at_download/file/file.pdf" ' \
            'target="_self" title=""><img src="http://nohost/plone/pdf.png" ' \
            'class="attachmentLinkIcon"/> internal link (pdf, 8.4 KB)</a></p>' \
            % file_obj.UID()
        parsed_html = self.output_filter(html)
        self.assertIn('<img src="http://nohost/plone/pdf.png" class="attachmentLinkIcon"/>', parsed_html)  # noqa
        self.assertIn('internal link (pdf, 8.4 KB)', parsed_html)
        self.assertEqual(parsed_html, new_html)

    def test_filter_with_link_to_image(self):
        """Test if the filter works properly with a link to an image"""
        img_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            file=open(img_path))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/%s" target="_self" ' \
            'title="">internal link</a></p>' % image.UID()
        new_html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an <a class="internal-link" href="resolveuid/%s" ' \
            'target="_self" title=""><img src="http://nohost/plone/image.png"' \
            ' class="attachmentLinkIcon"/> internal link (jpg, 5.0 KB)</a></p>'\
            % image.UID()
        parsed_html = self.output_filter(html)
        self.assertIn('<img src="http://nohost/plone/image.png" class="attachmentLinkIcon"/>', parsed_html)  # noqa
        self.assertIn('internal link (jpg, 5.0 KB)', parsed_html)
        self.assertEqual(parsed_html, new_html)
