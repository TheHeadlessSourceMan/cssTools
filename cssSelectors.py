"""
Decode, match, and find Css Selectors
"""
import typing
import re
from .htmlTypes import HtmlElementLike


CssSelectorCompatible=typing.Union[str,"CssSelector"]
SelectorCompatible=CssSelectorCompatible
CssSelectorsCompatible=typing.Union[str,CssSelectorCompatible,"CssSelectors",
    typing.Iterable[typing.Union[str,CssSelectorCompatible,"CssSelectors"]]]
SelectorsCompatible=CssSelectorsCompatible

class CssSelectorRequirement:
    """
    Part of a css selector
    """
    PART_SPLITTER_RE=re.compile(r"""([.@])?([0-9a-z_]+)""",re.DOTALL|re.IGNORECASE)

    def __init__(self,match:typing.Union[None,str,typing.Match[str]]):
        """
        """
        self._matchString=''
        self._nameMatchRe:typing.Union[None,str,typing.Pattern[str]]=None
        self._attributeMatchRe:typing.Dict[
            typing.Union[str,typing.Pattern[str]],
            typing.Union[str,typing.Pattern[str]]]={} # attributeName,attributeValue
        if match is not None:
            self.assign(match)

    def assign(self,matchString:typing.Union[str,typing.Match[str]])->None:
        """
        Assign the value of this object
        """
        if isinstance(matchString,str):
            match=self.PART_SPLITTER_RE.split(matchString)
        else:
            match=matchString
            matchString=matchString.string
        if not match[0]:
            # a selector that is just text
            tagAttr=match[0].split('[')
            if tagAttr[0]:
                self._nameMatchRe=tagAttr[0]
            if len(tagAttr)>1:
                # has an attribute[] selector
                for attrMatch in tagAttr[1:]:
                    k,v=attrMatch.split('=',1)
                    self._attributeMatchRe[k]=v
            self._nameMatchRe=match[1]
        elif match[0]=='.': # a class selector
            # NOTE: any class matches are lumped in with _attributeMatchesRe
            self._attributeMatchRe['class']=match[1]

    def matches(self,element:HtmlElementLike)->bool:
        """
        Returns whether this matches the given element
        """
        if self._nameMatchRe is not None:
            if isinstance(self._nameMatchRe,str):
                if element.tagName!=self._nameMatchRe:
                    return False
            elif self._nameMatchRe.match(element.tagName) is None:
                return False
        attributes=element.attributes
        if self._attributeMatchRe:
            if attributes is None:
                return False
            foundOne=False
            for keyMatch,valueMatch in self._attributeMatchRe.items():
                # check all attributes to see if they match
                for k,v in attributes.items():
                    # check attribute name
                    if isinstance(keyMatch,str):
                        if keyMatch!=k:
                            continue
                    elif keyMatch.match(k) is None:
                        continue
                    # check attribute value
                    if isinstance(valueMatch,str):
                        if valueMatch!=v:
                            continue
                    elif valueMatch.match(v) is None:
                        continue
                    # it matched!
                    foundOne=True
                    break
                if foundOne:
                    break
        return True

    def __repr__(self)->str:
        return self._matchString


class CssSelector:
    """
    A CSS selector
    """

    def __init__(self,
        selector:typing.Optional[CssSelectorCompatible]=None):
        """
        """
        self._selectorString:str=''
        self._selectorRequirements:typing.List[CssSelectorRequirement]=[]
        if selector is not None:
            self.assign(selector)

    def __eq__(self,
        other:typing.Union[CssSelectorCompatible,HtmlElementLike]
        )->bool:
        if isinstance(other,(str,CssSelector)):
            return other==self._selectorString
        return self.matches(other)

    def matches(self,element:HtmlElementLike)->bool:
        """
        Returns whether this matches the given element
        """
        for requirement in self._selectorRequirements:
            if not requirement.matches(element):
                return False
        return True

    def assign(self,selector:CssSelectorCompatible):
        """
        Assign the value of this selector
        """
        if not isinstance(selector,str):
            selector=str(selector)
        self._selectorRequirements=[]
        for m in CssSelectorRequirement.PART_SPLITTER_RE.split(selector):
            self._selectorRequirements.append(CssSelectorRequirement(m))
Selector=CssSelector


class CssSelectors:
    """
    CSS selectors
    """

    def __init__(self,
        selectors:typing.Optional[CssSelectorsCompatible]=None):
        """
        """
        self._selectorsString:str=''
        self._selectors:typing.List[CssSelector]=[]
        if selectors is not None:
            self.assign(selectors)

    def __len__(self)->int:
        """
        Access like a list of Selector objects
        """
        return len(self._selectors)

    def __iter__(self)->typing.Iterator[CssSelector]:
        """
        Access like a list of Selector objects
        """
        return iter(self._selectors)

    @typing.overload
    def __getitem__(self,
        idx:int
        )->CssSelector:
        ...
    @typing.overload
    def __getitem__(self,
        idx:slice
        )->typing.Iterable[CssSelector]:
        ...
    def __getitem__(self,
        idx:typing.Union[int,slice]
        )->typing.Union[CssSelector,typing.Iterable[CssSelector]]:
        """
        Access like a list of Selector objects
        """
        return self._selectors[idx]

    def __eq__(self,
        other:typing.Union[CssSelectorsCompatible,HtmlElementLike]
        )->bool:
        if isinstance(other,(str,CssSelectors)):
            return other==self._selectorsString
        return self.matches(other)

    def matches(self,element:HtmlElementLike)->bool:
        """
        Returns whether this matches the given element
        """
        for selector in self._selectors:
            if selector.matches(element):
                return True
        return False

    def assign(self,selectors:typing.Optional[CssSelectorsCompatible]):
        """
        Assign the value of this selector
        """
        self._selectors=[]
        self.addCssSelectors(selectors)

    def addCssSelectors(self,selectors:typing.Optional[CssSelectorsCompatible]):
        """
        Add selectors
        """
        if selectors is None:
            return
        if isinstance(selectors,str):
            for s in selectors.split(','):
                self.addCssSelectors(CssSelector(s))
        elif isinstance(selectors,CssSelector):
            self._selectors.append(selectors)
        elif isinstance(selectors,CssSelectors):
            self.extend(selectors)
        else:
            for selector in selectors:
                self.addCssSelectors(selector)
    addSelectors=addCssSelectors
    addCssSelector=addCssSelectors
    addSelector=addCssSelectors
    add=addCssSelectors
    append=addCssSelectors
    extend=addCssSelectors

    def removeCssSelectors(self,selectors:typing.Optional[CssSelectorsCompatible]):
        """
        Remove any number of selectors
        """
        if selectors is None:
            return
        if isinstance(selectors,str):
            for s in selectors.split(','):
                self._selectors.remove(CssSelector(s))
        elif isinstance(selectors,CssSelector):
            self._selectors.remove(selectors)
        else:
            for selector in selectors:
                self.removeCssSelectors(selector)
    removeSelectors=removeCssSelectors
    removeCssSelector=removeCssSelectors
    removeSelector=removeCssSelectors
    remove=removeCssSelectors
    __delitem__=removeCssSelectors
Selectors=CssSelectors
