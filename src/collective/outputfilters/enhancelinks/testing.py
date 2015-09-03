# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.outputfilters.enhancelinks


class CollectiveOutputfiltersenhancelinksLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.outputfilters.enhancelinks)

    # def setUpPloneSite(self, portal):
    #     applyProfile(portal, 'collective.outputfilters.enhancelinks:default')


COLLECTIVE_OUTPUTFILTERS_enhancelinks_FIXTURE = CollectiveOutputfiltersenhancelinksLayer()


COLLECTIVE_OUTPUTFILTERS_enhancelinks_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_OUTPUTFILTERS_enhancelinks_FIXTURE,),
    name='CollectiveOutputfiltersenhancelinksLayer:IntegrationTesting'
)


COLLECTIVE_OUTPUTFILTERS_enhancelinks_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_OUTPUTFILTERS_enhancelinks_FIXTURE,),
    name='CollectiveOutputfiltersenhancelinksLayer:FunctionalTesting'
)


COLLECTIVE_OUTPUTFILTERS_enhancelinks_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_OUTPUTFILTERS_enhancelinks_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveOutputfiltersenhancelinksLayer:AcceptanceTesting'
)
