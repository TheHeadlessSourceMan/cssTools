"""
Used to streamline CSS searching by extracting element
id,class,and tag name into their appropriate CSS selectors
"""
import typing
from xml.dom.minidom import Element
import cssTools


SearchNuggetCompatible=typing.Union['SearchNugget',Element]
def asSearchNugget(nugg:SearchNuggetCompatible)->'SearchNugget':
    """
    Always returns a SearchNugget object.
    if nugg is already a SearchNugget object,
        returns unchanged

    :param nugg: something to make into a SearchNugget
    :type nugg: SearchNuggetCompatible
    :return: always a SearchNugget
    :rtype: SearchNugget
    """
    if isinstance(nugg,SearchNugget):
        return nugg
    return SearchNugget(nugg)


class SearchNugget:
    """
    Used to streamline CSS searching by extracting element
    id,class,and tag name into their appropriate CSS selectors
    """
    def __init__(self,domElement:Element):
        self.rulesMatched:cssTools.CssRule=[] # keep track of which rules matched, in order!
        self._domElement=domElement
        self._idSelector=domElement.attrib.get('id',None)
        if self._idSelector is not None:
            self._idSelector='@'+self._idSelector
        self._tagSelector=domElement.tagName
        self._classSelector=domElement.attrib.get('class',None)
        if self._classSelector is not None:
            self._classSelector='.'+self._classSelector