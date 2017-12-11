==============================================================================
collective.outputfilters.enhancelinks
==============================================================================

.. image:: https://travis-ci.org/PloneGov-IT/collective.outputfilters.enhancelinks.svg?branch=master
    :target: https://travis-ci.org/PloneGov-IT/collective.outputfilters.enhancelinks

This product add a new outputfilter that generates additional informations for
Tiny MCE's internal link.

It's a substitute of `collective.tinymceplugins.advfilelinks`__,
that doesn't work with Plone >= 4.3 because it uses Products.TinyMCE >= 1.3.

.. contents:: **Table of contents**


Features
--------
For every link that points to an internal content (file or image),
in the rendered html will be added some new informations:

- The mimetype icon before the link text
- The mimetype and filesize after the link text
- The url of a File points to the direct download


Installation
------------

Install collective.outputfilters.enhancelinks by adding it to your buildout::

   [buildout]

    ...

    eggs =
        collective.outputfilters.enhancelinks


and then run "bin/buildout".


It doesn't need to be installed.

Extending content-types
-----------------------

This product is modular, so if you want to add this feature (or more features)
to some custom content-types you only need to provide a new adapter for the ``ILinkEnhancerProvider`` interface::

    <adapter
        for="your.package.interfaces.IYourContent"
        provides="collective.outputfilters.enhancelinks.interfaces.ILinkEnhancerProvider"
        factory=".adapters.YourContentEnhanceLink"
    />

Then provide the Python adapter code::

    from collective.outputfilters.enhancelinks.adapters import BaseEnhanceLink

    class YourContentEnhanceLink(BaseEnhanceLink):
        ...

There are 4 basic methods for a basic override::

    def get_url_suffix(filename):
        """ Return additional suffix to append at the end of the url """

    def get_icon_url(mime_infos):
        """ Return the correct mimetype icon url """

    def get_extension(content_file, mime_infos):
        """ Return the filename extension"""

    def get_formatted_size(content_file):
        """ Return a formatted file size """


Additional mimetype icons
-------------------------
If you want more mimetype icons (for example for OpenOffice documents),
you could add and install `collective.mtrsetup`__ in your buildout.

__ http://pypi.python.org/pypi/collective.mtrsetup


Contribute
----------

- Issue Tracker: https://github.com/PloneGov-IT/collective.outputfilters.enhancelinks/issues
- Source Code: https://github.com/PloneGov-IT/collective.outputfilters.enhancelinks


Compatibility
-------------

This product has been tested on:

* Plone 4.2
* Plone 4.3
* Plone 5.0
* Plone 5.1

It works with Archetype-based and Dexterity-based (`plone.app.contenttypes`__)
standard File and Image content-types.

__ http://pypi.python.org/pypi/plone.app.contenttypes


License
-------

The project is licensed under the GPLv2.


Credits
-------

Developed with the support of:

* `Regione Emilia Romagna`__


All of them supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/


Authors
-------

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
