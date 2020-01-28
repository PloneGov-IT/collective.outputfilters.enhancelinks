# -*- coding: utf-8 -*-
from collective.outputfilters.enhancelinks.interfaces import (
    ILinkEnhancerProvider,
)
from humanfriendly import format_size
from plone import api
from zope.interface import implementer

import mimetypes
import six


@implementer(ILinkEnhancerProvider)
class BaseEnhanceLink(object):
    def __init__(self, context):
        self.context = context

    def get_url_suffix(self, filename):
        return ""

    def get_icon_url(self, mime_infos):
        portal_url = api.portal.get().absolute_url()
        return "{0}/{1}".format(portal_url, mime_infos.icon_path)

    def get_extension(self, content_file, mime_infos):
        extension = content_file.filename.split(".")[-1]
        mime_extensions = self.get_right_mime_extensions(mime_infos)
        if extension in mime_extensions:
            return extension
        return

    def guess_mimetype(self, filetype, filename):
        """
        Return a list of possible mimetypes of the given file from
        mimetypes registry
        """
        mtr = api.portal.get_tool(name="mimetypes_registry")
        mime = list(mtr.lookup(filetype))
        if not mime and filename:
            mime.append(mtr.lookupExtension(filename))
        # mime.append(mtr.lookup("application/octet-stream")[0])
        return mime

    def get_right_mime_extensions(self, mime_infos):
        """ Two jobs for this method:
        a. It seems that if you `lookup` the  `text/csv` MIME type with the
        mimetypes_registry, the informations retrived are incomplete
        (the object returned, for example, doesn't have any extension
        specified). To avoid this problem, we add one more check using the
        standard mimetypes python library. (RER rm#20156)

        b. Remove dots from extensions if any.
        """
        exts = []

        if not mime_infos.extensions:
            for mimetype in mime_infos.mimetypes:
                if mimetypes.guess_extension(mimetype):
                    exts.append(
                        mimetypes.guess_extension(mimetype).replace(".", "")
                    )
            return tuple(exts)
        else:
            without_dots = [x.replace(".", "") for x in mime_infos.extensions]
            return tuple(without_dots)

    def get_formatted_size(self, content_file):
        # allow arbitrary sizes to be passed through,
        # if there is no size, but there is an object
        # look up the object, this maintains backwards
        # compatibility
        if hasattr(content_file, "get_size"):
            size = content_file.get_size()
        elif hasattr(content_file, "size"):
            size = content_file.size
        elif hasattr(content_file, "getSize"):
            size = content_file.getSize()
        # if the size is a float, then make it an int
        # happens for large files
        try:
            size = int(size)
        except (ValueError, TypeError):
            return ""
        return format_size(size)

    def extract_infos(self, content_file, mime):
        """
        Extract infos from a list of given mimetypes
        """
        result = {}
        for mime_infos in mime:
            # set icon_url
            if hasattr(mime_infos, "icon_path") and not result.get("icon_url"):
                result["icon_url"] = self.get_icon_url(mime_infos)
            # set extension
            if not result.get("extension"):
                result["extension"] = self.get_extension(
                    content_file, mime_infos
                )
        # set size
        result["size"] = self.get_formatted_size(content_file)
        result["url_suffix"] = self.get_url_suffix(content_file.filename)
        return result


class ATFileEnhanceLink(BaseEnhanceLink):
    def get_link_details(self):
        """
        Return some additional details from given content
        """
        content_file = self.context.getFile()
        if not content_file:
            return {}
        mime = self.guess_mimetype(
            content_file.getContentType(), content_file.filename
        )
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)

    def get_url_suffix(self, filename):
        return "/at_download/file/{0}".format(filename)


class ATImageEnhanceLink(ATFileEnhanceLink):
    def get_url_suffix(self, filename):
        return ""


class DXFileEnhanceLink(BaseEnhanceLink):
    def get_link_details(self):
        """
        Return some additional details from given content
        """
        content_file = self.context.file
        if not content_file:
            return {}
        mime = self.guess_mimetype(
            content_file.contentType, content_file.filename
        )
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)

    def get_url_suffix(self, filename):
        if six.PY2:
            filename = filename.encode("utf-8")
        return "/@@download/file/{0}".format(filename)


class DXImageEnhanceLink(BaseEnhanceLink):
    def get_link_details(self):
        """
        Return some additional details from given content
        """
        content_file = self.context.image
        if not content_file:
            return {}
        mime = self.guess_mimetype(
            content_file.contentType, content_file.filename
        )
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)
