# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.outputfilters.enhancelinks.enhance_links import EnhanceLinks
from collective.outputfilters.enhancelinks.tests.base import BaseTest
from collective.outputfilters.enhancelinks.testing import COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


class TestFilter(BaseTest):
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
            '<p>This is an <a class="external-link" href="https://plone.org" '\
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
            '<a class="internal-link" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(document.UID())
        self.assertEqual(self.output_filter(html), html)

    def test_filter_with_link_to_file(self):
        """Test if the filter works properly with a link to a file"""
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a data-linktype="internal" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(file_obj.UID())
        parsed_html = self.output_filter(html)
        self.assertIn(self.file_icon_compare_str(), parsed_html)  # noqa
        self.assertIn('internal link (pdf, 8.4 KB)', parsed_html)

    def test_filter_skip_with_link_to_file(self):
        """
        Test if the filter works properly with a link to a file and skip a link
        without internal-link class
        """
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="foo" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(file_obj.UID())
        parsed_html = self.output_filter(html)
        self.assertNotIn(self.image_icon_compare_str(), parsed_html)  # noqa
        self.assertNotIn('internal link (pdf, 8.4 KB)', parsed_html)

    def test_filter_with_link_to_image(self):
        """Test if the filter works properly with a link to an image"""
        image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            image=self.get_attachment(u'image.jpg', type='image'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a data-linktype="internal" href="resolveuid/{0}" target="_self"'\
            ' title="">internal link</a></p>'.format(image.UID())
        parsed_html = self.output_filter(html)
        self.assertIn(self.image_icon_compare_str(), parsed_html)  # noqa
        self.assertIn('internal link (jpg, 5.0 KB)', parsed_html)

    def test_filter_with_oldstyle_link_to_document(self):
        """Test if the filter does nothing without hrefs in html"""
        document = api.content.create(
            type='Document',
            title='A page',
            container=self.portal)
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(document.UID())
        self.assertEqual(self.output_filter(html), html)

    def test_filter_with_oldstyle_link_to_file(self):
        """Test if the filter works properly with a link to a file"""
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(file_obj.UID())
        parsed_html = self.output_filter(html)
        self.assertIn(self.file_icon_compare_str(), parsed_html)  # noqa
        self.assertIn('internal link (pdf, 8.4 KB)', parsed_html)

    def test_filter_with_oldstyle_link_to_file_multiple_classes(self):
        """
        Test if the filter works properly with a link to a file and
        have multiple css classes
        """
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link some-class" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(file_obj.UID())
        parsed_html = self.output_filter(html)
        self.assertIn(self.file_icon_compare_str(), parsed_html)  # noqa
        self.assertIn('internal link (pdf, 8.4 KB)', parsed_html)

    def test_filter_skip_with_oldstyle_link_to_file(self):
        """
        Test if the filter works properly with a link to a file and skip a link
        without internal-link class
        """
        file_obj = api.content.create(
            type='File',
            title='file',
            container=self.portal,
            file=self.get_attachment(u'file.pdf', type='file'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="foo" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(file_obj.UID())
        parsed_html = self.output_filter(html)
        self.assertNotIn(self.file_icon_compare_str(), parsed_html)  # noqa
        self.assertNotIn('internal link (pdf, 8.4 KB)', parsed_html)

    def test_filter_with_oldstyle_link_to_image(self):
        """Test if the filter works properly with a link to an image"""
        image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            image=self.get_attachment(u'image.jpg', type='image'))
        html = '<p>This is a simple <strong>formatted text</strong>.</p>' \
            '<p>This is an ' \
            '<a class="internal-link" href="resolveuid/{0}" target="_self" ' \
            'title="">internal link</a></p>'.format(image.UID())
        parsed_html = self.output_filter(html)
        self.assertIn(self.image_icon_compare_str(), parsed_html)  # noqa
        self.assertIn('internal link (jpg, 5.0 KB)', parsed_html)
