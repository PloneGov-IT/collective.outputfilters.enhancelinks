# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.outputfilters.enhancelinks.interfaces import (
    ILinkEnhancerProvider,
)  # noqa
from collective.outputfilters.enhancelinks.testing import (
    COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING,
)  # noqa
from collective.outputfilters.enhancelinks.tests.base import BaseTest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


FILE_ICON_URLS = [
    'http://nohost/plone/pdf.png',
    'http://nohost/plone/++resource++mimetype.icons/pdf.png',
]

CSV_ICON_URLS = [
    'http://nohost/plone/svg.png',
    'http://nohost/plone/++resource++mimetype.icons/svg.png',
    'http://nohost/plone/++resource++mimetype.icons/text.png',  # see below
]

IMAGE_ICON_URLS = [
    'http://nohost/plone/image.png',
    'http://nohost/plone/++resource++mimetype.icons/image.png',
]

FILE_DOWNLOAD_URLS = [
    '/at_download/file/file.pdf',
    '/@@download/file/file.pdf',
]

CSV_DOWNLOAD_URLS = [
    '/at_download/file/file_csv.csv',
    '/@@download/file/file_csv.csv',
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
            file=self.get_attachment(u'file.pdf', type='file'),
        )
        self.csv = api.content.create(
            type='File',
            title='csv file',
            container=self.portal,
            file=self.get_attachment(u'file_csv.csv', type='file'),
        )
        self.image = api.content.create(
            type='Image',
            title='image',
            container=self.portal,
            image=self.get_attachment(u'image.jpg', type='image'),
        )
        self.document = api.content.create(
            type='Document', title='A page', container=self.portal
        )
        self.file_provider = ILinkEnhancerProvider(self.file, None)
        self.csv_provider = ILinkEnhancerProvider(self.csv, None)
        self.img_provider = ILinkEnhancerProvider(self.image, None)

    def test_adapter_guess_mimetype(self):
        """Test if the method find the correct mimetype"""
        # I pass False because it isn't a DX content
        file_item = self.get_right_file(item=self.file, type='file')
        csv_item = self.get_right_file(item=self.csv, type='file')
        image_item = self.get_right_file(item=self.image, type='image')

        # File PDF
        mimetype = self.extract_mimetype(file_item)
        self.assertEqual(len(mimetype), 1)
        self.assertEqual(mimetype[0].id, 'PDF document')

        # Csv
        mimetype = self.extract_mimetype(csv_item)
        self.assertEqual(len(mimetype), 1)
        # ===================== WARNING ==================================
        # ATTENZIONE: questo singolo test è 'sbagliato': il vero risultato
        # dovrebbe essere `CSV document` ma il prodotto
        # `Products.MimetypesRegistry` ha il mimetype sbagliato e ho aperto
        # anche una issue su questo argomento
        # https://github.com/plone/Products.MimetypesRegistry/issues/17
        # Quando questo test fallirà, probabilmente sarà stato aggiornato
        # e sarà da sistemare anche questo test.
        self.assertEqual(mimetype[0].id, 'text/comma-separated-values')

        # Image
        img_mimetype = self.extract_mimetype(image_item)
        self.assertEqual(len(img_mimetype), 1)
        self.assertEqual(img_mimetype[0].id, 'JPEG image')

    def test_adapter_format_obj_size(self):
        """Test if the method returns a correct obj size"""
        # File PDF
        self.assertEqual(
            self.file_provider.get_formatted_size(self.file.file), '8.56 KB'
        )
        # CSV
        self.assertEqual(
            self.csv_provider.get_formatted_size(self.csv.file), '39 bytes'
        )
        # Image
        self.assertEqual(
            self.img_provider.get_formatted_size(self.image.image), '5.13 KB'
        )

    def test_adapter_extract_infos_from_mime(self):
        """" Test if the method returns the correct infos """
        file_item = self.get_right_file(item=self.file, type='file')
        csv_item = self.get_right_file(item=self.csv, type='file')
        image_item = self.get_right_file(item=self.image, type='image')

        # File PDF
        mimetype = self.extract_mimetype(file_item)
        infos = self.file_provider.extract_infos(file_item, mimetype)
        self.assertIn(infos.get('icon_url'), FILE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.56 KB')
        self.assertIn(infos.get('url_suffix'), FILE_DOWNLOAD_URLS)

        # CSV
        mimetype = self.extract_mimetype(csv_item)
        infos = self.csv_provider.extract_infos(csv_item, mimetype)
        # La successiva assertIn è strana per lo stesso motivo del WARNING che
        # potete trovare nei commenti più su. Il rilevamento del csv è buggato
        # e quindi l'icona restituita è 'text.png' che non è necessariamente
        # sbagliata però si potrebbe fare di meglio.
        self.assertIn(infos.get('icon_url'), CSV_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'csv')
        self.assertEqual(infos.get('size'), '39 bytes')
        self.assertIn(infos.get('url_suffix'), CSV_DOWNLOAD_URLS)

        # Image
        img_mimetype = self.extract_mimetype(image_item)
        infos = self.img_provider.extract_infos(image_item, img_mimetype)
        self.assertIn(infos.get('icon_url'), IMAGE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.13 KB')
        self.assertEqual(infos.get('url_suffix'), '')

    def test_adapter_for_file(self):
        """Test if the view returns the correct infos for a file"""
        infos = self.file_provider.get_link_details()
        self.assertIn(infos.get('icon_url'), FILE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'pdf')
        self.assertEqual(infos.get('size'), '8.56 KB')
        self.assertIn(infos.get('url_suffix'), FILE_DOWNLOAD_URLS)

    def test_adapter_for_csv(self):
        """Test if the view returns the correct infos for a file"""
        infos = self.csv_provider.get_link_details()
        self.assertIn(infos.get('icon_url'), CSV_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'csv')
        self.assertEqual(infos.get('size'), '39 bytes')
        self.assertIn(infos.get('url_suffix'), CSV_DOWNLOAD_URLS)

    def test_adapter_for_image(self):
        """Test if the view returns the correct infos for an image"""
        infos = self.img_provider.get_link_details()
        self.assertIn(infos.get('icon_url'), IMAGE_ICON_URLS)
        self.assertEqual(infos.get('extension'), 'jpg')
        self.assertEqual(infos.get('size'), '5.13 KB')
        self.assertEqual(infos.get('url_suffix'), '')
