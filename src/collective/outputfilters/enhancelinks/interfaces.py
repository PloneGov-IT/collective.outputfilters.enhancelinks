# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface


class ILinkEnhancerProvider(Interface):

    def get_link_details():
        """
        Return some additional details from given content
        """
    def get_url_suffix(filename):
        """ Return additional suffix to append at the end of the url """

    def get_icon_url(mime_infos):
        """ Return the correct mimetype icon url """

    def get_extension(content_file, mime_infos):
        """ Return the filename extension"""

    def get_formatted_size(content_file):
        """ Return a formatted file size """
