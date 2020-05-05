# -*- coding: utf-8 -*-
from collective.outputfilters.enhancelinks import logger
from collective.outputfilters.enhancelinks.interfaces import (
    ILinkEnhancerProvider,
)
from lxml import etree
from lxml import html
from plone import api
from plone.outputfilters.filters.resolveuid_and_caption import (
    IResolveUidsEnabler,
)  # noqa
from plone.outputfilters.filters.resolveuid_and_caption import resolveuid_re
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getAllUtilitiesRegisteredFor
import six


class EnhanceLinks(object):
    """
    Filter implementation. Add more informations in links
    """

    order = 600

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request
        self.data = u""

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
        if not isinstance(data, six.text_type):
            data = data.decode("utf-8")
        created_parent = False
        try:
            tree = html.fragment_fromstring(data, create_parent=False)
        except etree.ParserError:
            tree = html.fragment_fromstring(data, create_parent=True)
            created_parent = True
        except AssertionError as e:
            logger.exception(e)
            logger.warning(
                "Transformation not applied in {0}".format(
                    self.context.absolute_url()
                )
            )
            return None
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
        if not node.get("href"):
            return None

        match = resolveuid_re.match(node.get("href"))
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
        additional_infos = [
            x
            for x in (link_details.get("extension"), link_details.get("size"))
            if x
        ]
        if node.getchildren():
            child = node.getchildren()[-1]
            if child.tail:
                child_postfix_text = child.tail
            else:
                child_postfix_text = ""
            additional_infos = " ({0})".format(", ".join(additional_infos))
            child_postfix_text = child_postfix_text + additional_infos
            child.tail = child_postfix_text
        elif additional_infos and text:
            additional_infos = " ({0})".format(", ".join(additional_infos))
            text = text + additional_infos
        if link_details.get("icon_url"):
            icon_tag = etree.Element("img")
            icon_tag.set("src", link_details.get("icon_url"))
            icon_tag.set("class", "attachmentLinkIcon")
            node.insert(0, icon_tag)
        if text:
            # move text after the image
            icon_tag.tail = text
            node.text = ""
        else:
            icon_tag.tail = " "
            node_children = node.getchildren()
            if node_children and not node_children[-1].tail:
                node_children[-1].tail = " ({0})".format(
                    ", ".join(additional_infos)
                )
        if link_details.get("url_suffix"):
            self.update_href(node, link_details)

    def update_href(self, node, link_details):
        if six.PY2:
            href = node.get("href").encode("utf-8")
        else:
            href = node.get("href")
        if link_details.get("url_suffix") in href:
            # suffix is already present in the link, so skip it
            return
        try:
            new_url = "{0}{1}".format(
                node.get("href"), link_details.get("url_suffix")
            )
        except (UnicodeDecodeError, UnicodeEncodeError):
            new_url = "{0}{1}".format(href, link_details.get("url_suffix"))
            new_url = new_url.decode("utf-8")
        try:
            node.set("href", new_url)
        except ValueError:
            node.set("href", new_url.decode("utf-8"))

    def process(self, data):
        """
        Process data and check links infos.
        Parse only internal links
        """
        self.data = data
        if not self.resolve_uids:
            # we can't resolve uids, we can't do anything
            return
        root_node = self.generate_xml(data)
        if root_node is None:
            return
        # old-style links
        links = set(
            root_node.xpath(
                '//a[contains(concat(" ", @class, " "), " internal-link ")]'
            )
        )
        # new-style links
        links.update(root_node.xpath('//a[@data-linktype="internal"]'))
        if not links:
            # there aren't links in this html snippet
            return
        for node in links:
            self.enhance_node_infos(node)
        # generate the new html
        raw_html = ""
        for tag in root_node.getchildren():
            tag_html = etree.tostring(tag, encoding="utf-8", method="html")
            if six.PY3:
                tag_html = tag_html.decode('utf-8')
            raw_html += tag_html
            tail = tag.tail
            if tail:
                if isinstance(tail, six.text_type):
                    tail = tail.encode("utf-8")
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
