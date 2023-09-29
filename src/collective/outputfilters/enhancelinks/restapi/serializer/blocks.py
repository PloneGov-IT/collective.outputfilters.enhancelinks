from collective.outputfilters.enhancelinks.interfaces import ICollectiveOutputfiltersEnhancelinksLayer
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import ResolveUIDSerializer
from plone.restapi.serializer.utils import resolve_uid
from plone.restapi.serializer.utils import uid_to_url
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ResolveUIDSerializerBaseWithPortalType(ResolveUIDSerializer):
    order = -1

    def _process_data(self, data, field=None):
        if isinstance(data, str) and field in self.fields:
            return uid_to_url(data)
        if isinstance(data, list):
            return [
                self._process_data(data=value, field=field) for value in data
            ]
        if isinstance(data, dict):
            fields = ["value"] if data.get("@type") == "URL" else []
            fields.append("@id")
            fields.extend(self.fields)
            newdata = {}
            for field in fields:
                if field not in data or not isinstance(data[field], str):
                    continue
                newdata[field], brain = resolve_uid(data[field])
                if brain is not None and "image_scales" not in newdata:
                    newdata["image_scales"] = getattr(
                        brain, "image_scales", None
                    )
                newdata["content_info"] = {
                    "portal_type": brain and brain.portal_type or None,
                    "size": brain and brain.getObjSize,
                }

            result = {
                field: (
                    newdata[field]
                    if field in newdata
                    else self._process_data(
                        data=newdata.get(field, value), field=field
                    )
                )
                for field, value in data.items()
            }
            if newdata.get("image_scales"):
                result["image_scales"] = newdata["image_scales"]
            if newdata.get("content_info"):
                result["content_info"] = newdata["content_info"]
            return result
        return data
