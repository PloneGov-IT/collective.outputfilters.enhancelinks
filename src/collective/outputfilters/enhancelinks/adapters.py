# -*- coding: utf-8 -*-
from zope.interface import implements
from plone import api
from collective.outputfilters.enhancelinks.interfaces import ILinkEnhancerProvider

SIZE_CONST = {
    'KB': 1024,
    'MB': 1024 * 1024,
    'GB': 1024 * 1024 * 1024}
SIZE_ORDER = ('GB', 'MB', 'KB')


class BaseEnhanceLink(object):
    implements(ILinkEnhancerProvider)

    def __init__(self, context):
        self.context = context

    def get_url_suffix(self, filename):
        return ""

    def get_icon_url(self, mime_infos):
        portal_url = api.portal.get().absolute_url()
        return portal_url + "/" + mime_infos.icon_path

    def get_extension(self, content_file, mime_infos):
        extension = content_file.filename.split(".")[-1]
        if extension in mime_infos.extensions:
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

    def get_formatted_size(self, content_file):
        smaller = SIZE_ORDER[-1]
        # allow arbitrary sizes to be passed through,
        # if there is no size, but there is an object
        # look up the object, this maintains backwards
        # compatibility
        if hasattr(content_file, 'get_size'):
            size = content_file.get_size()
        elif hasattr(content_file, 'size'):
            size = content_file.size
        # if the size is a float, then make it an int
        # happens for large files
        try:
            size = int(size)
        except (ValueError, TypeError):
            return ""
        if not size:
            return ""
        if size < SIZE_CONST[smaller]:
            return '1 %s' % smaller
        for c in SIZE_ORDER:
            if size / SIZE_CONST[c] > 0:
                break
        return '%.1f %s' % (float(size / float(SIZE_CONST[c])), c)

    def extract_infos(self, content_file, mime):
        """
        Extract infos from a list of given mimetypes
        """
        result = {}
        for mime_infos in mime:
            # set icon_url
            if hasattr(mime_infos, 'icon_path') and not result.get('icon_url'):
                result['icon_url'] = self.get_icon_url(mime_infos)
            # set extension
            if hasattr(mime_infos, 'extensions') and not result.get('extension'):
                result['extension'] = self.get_extension(
                    content_file,
                    mime_infos)
        # set size
        result['size'] = self.get_formatted_size(content_file)
        result['url_suffix'] = self.get_url_suffix(content_file.filename)
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
            content_file.getContentType(),
            content_file.filename)
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)

    def get_url_suffix(self, filename):
        return "/at_download/file/%s" % filename


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
            content_file.contentType,
            content_file.filename)
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)

    def get_url_suffix(self, filename):
        return "/@@download/file/%s" % filename


class DXImageEnhanceLink(BaseEnhanceLink):

    def get_link_details(self):
        """
        Return some additional details from given content
        """
        content_file = self.context.image
        if not content_file:
            return {}
        mime = self.guess_mimetype(
            content_file.contentType,
            content_file.filename)
        if not mime:
            return {}
        return self.extract_infos(content_file, mime)
