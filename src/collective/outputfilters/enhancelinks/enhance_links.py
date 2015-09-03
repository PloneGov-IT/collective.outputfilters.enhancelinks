from lxml import html
from lxml import etree

from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getAllUtilitiesRegisteredFor
from plone.outputfilters.filters.resolveuid_and_caption import IResolveUidsEnabler
from plone.outputfilters.filters.resolveuid_and_caption import resolveuid_re
from plone import api
import re
from collective.outputfilters.enhancelinks.interfaces import ILinkEnhancerProvider
import pkg_resources
from collective.outputfilters.enhancelinks import logger


class EnhanceLinks(object):
    """
    Filter implementation. Add more informations in links
    """
    order = 600

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request
        self.data = u''

    @lazy_property
    def resolve_uids(self):
        for u in getAllUtilitiesRegisteredFor(IResolveUidsEnabler):
            if u.available:
                return True
        return False

    def generate_xml(self, data):
        """
        Transform the given html string into xml
        """
        if not isinstance(data, unicode):
            data = data.decode("utf-8")
        created_parent = False
        try:
            tree = html.fragment_fromstring(data, create_parent=False)
        except etree.ParserError:
            tree = html.fragment_fromstring(data, create_parent=True)
            created_parent = True

        if not created_parent:
            root_node = etree.Element("div")
            root_node.append(tree)
        else:
            root_node = tree
        return root_node

    def get_obj_from_link(self, node):
        """
        Try to get the object from the href
        """
        match = resolveuid_re.match(node.get('href'))
        if not match:
            return None
        uid, _subpath = match.groups()
        obj = api.content.get(UID=uid)
        return obj

    def enhance_node_infos(self, node):
        """
        Add additional infos, if the node needs them
        """
        text = node.text
        obj = self.get_obj_from_link(node)
        if not obj:
            # the url is broken!
            return
        enhancer_provider = ILinkEnhancerProvider(obj, None)
        if not enhancer_provider:
            # there isn't an adapter registered for this content-type
            return
        link_details = enhancer_provider.get_link_details()
        if not link_details:
            return
        additional_infos = [x for x in (
            link_details.get('extension'),
            link_details.get('size')) if x]
        if additional_infos:
            text = " %s (%s)" % (text, ", ".join(additional_infos))
        if link_details.get('icon_url'):
            icon_tag = etree.Element("img")
            icon_tag.set("src", link_details.get('icon_url'))
            icon_tag.set("class", "attachmentLinkIcon")
            # move text after the image
            icon_tag.tail = text
            node.insert(0, icon_tag)
            node.text = ""
        if link_details.get('url_suffix'):
            node.set('href', node.get('href') + link_details.get('url_suffix'))

    def process(self, data):
        """
        Process data and check links infos
        """
        self.data = data
        if not self.resolve_uids:
            # we can't resolve uids, we can't do anything
            return
        root_node = self.generate_xml(data)
        if root_node is None:
            return
        links = root_node.xpath('//*[@href]')
        if not links:
            # there aren't links in this html snippet
            return
        for node in links:
            self.enhance_node_infos(node)
        # generate the new html
        raw_html = ''
        for tag in root_node.getchildren():
            raw_html += etree.tostring(tag, encoding='utf-8')
            tail = tag.tail
            if tail:
                if isinstance(tail, unicode):
                    tail = tail.encode('utf-8')
                raw_html += tail
        self.data = raw_html

    def is_enabled(self):
        if self.context is None:
            return False
        else:
            return True

    def getResult(self):
        """Return the parsed result and flush it"""
        return self.data

    def __call__(self, data):
        self.process(data)
        return self.getResult()
