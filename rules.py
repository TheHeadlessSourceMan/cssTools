"""
A single formatting rule

A rule consists of a series of selectors and
a series of CssStyles that they all map to
"""
import typing
from htmlTypes import HtmlElementLike
from .cssStyles import CssStyles,CssStylesCompatible
from .cssSelectors import CssSelector,CssSelectors,CssSelectorsCompatible,CssSelectorCompatible

class CssRule:
    """
    A single formatting rule

    A rule consists of a series of selectors and
    a series of CssStyles that they all map to
    """

    def __init__(self,
        selectors:CssSelectorsCompatible,
        styles:CssStylesCompatible):
        """ """
        self._styles:CssStyles=CssStyles(styles)
        self.selectors=CssSelectors(selectors)

    @property
    def styles(self)->CssStyles:
        """
        The style associated with this rule
        """
        return self._styles
    @styles.setter
    def styles(self,styles:CssStylesCompatible):
        self._styles:CssStyles=CssStyles(styles)
    @property
    def style(self)->CssStyles:
        """
        The style associated with this rule
        """
        return self._styles
    @style.setter
    def style(self,styles:CssStylesCompatible):
        self._styles:CssStyles=CssStyles(styles)

    @property
    def numSelectors(self)->int:
        """
        number of selectors
        """
        return len(self.selectors)

    def hasSelector(self,selector:typing.Optional[CssSelectorCompatible])->bool:
        """
        See if the given selector is present in the set of selectors

        :param selector: [description]
        :type selector: str
        :return: [description]
        :rtype: bool
        """
        if selector is None:
            return False
        for sel in self.selectors:
            if sel==selector:
                return True
        return False

    def addCssSelectors(self,selector:CssSelectorsCompatible)->None:
        """
        Add more selectors
        """
        self.selectors.addCssSelectors(selector)
    addSelectors=addCssSelectors
    addSelector=addCssSelectors

    def removeSelector(self,selector:CssSelectorsCompatible)->None:
        """
        If the rule has the specified selector, remove it
        """
        try:
            self.selectors.remove(selector)
        except KeyError:
            pass

    def sameStyles(self,otherStyles:CssStylesCompatible)->bool:
        """
        Determine if the set of styles is the same as another
        set of styles.
        (Useful for things like reducing duplicates)
        """
        return self._styles==otherStyles

    def __eq__(self, # type: ignore
        other:typing.Union[None,str,"CssRule",cssTools.SearchNuggetCompatible]
        )->bool:
        """
        Does this match another item.

        If it's a Rule, then match the objects.
        It it's more html-like, determine if tf the tag matches.
        """
        if isinstance(other,str):
            # determine if it's css-like
            if other.find('<')<0:
                from .css import Css
                other=Css(data=other)[0]
            else:
                from htmlTools import Html
                other=Html(other)
        if isinstance(other,CssRule):
            if other.selectors!=self.selectors:
                return False
            if other._styles!=self._styles:
                return False
            return True
        return self.matches(other)

    def matches(self,nugg:cssTools.SearchNuggetCompatible)->bool:
        """
        Determine if this rule applies to the given selection
        :rtype: bool
        """
        nugg=cssTools.asSearchNugget(nugg)
        #TODO: css paths not supported, only simple Tag,.Class,@Id
        if nugg._idSelector in self._selectors: # pylint: disable=protected-access
            return True
        if nugg._classSelector in self._selectors: # pylint: disable=protected-access
            return True
        if nugg._tagSelector in self._selectors: # pylint: disable=protected-access
            return True
        return False

    def getStyles(self,
        nugg:cssTools.SearchNuggetCompatible
        )->typing.Optional[cssTools.CssStyles]:
        """
        collect all the styles that apply to a given element
        """
        nugg=cssTools.asSearchNugget(nugg)
        ret=None
        if self.matches(nugg):
            nugg.rulesMatched.append(self)
            ret=cssTools.CssStyles()
            for style in self._styles:
                ret.append(style)
        return ret

    def obfuscate(self,
        ignore:typing.Optional[typing.Dict]=None
        )->typing.Dict[str,str]:
        """
        ignore is used to skip values that have already been used

        returns {originalName:newName}
        """
        if ignore is None:
            ignore={}
        return {}


class CssRules:
    """
    A set of formatting rules.
    """

    def __init__(self,rules:typing.Iterable[CssRule]):
        self._rules:typing.List[CssRule]=list(rules)

    def getRulesForElement(self,element:HtmlElementLike)->typing.Iterable[CssRule]:
        """
        get all rules that apply to a given element
        """
        for rule in self._rules:
            if rule.matches(element):
                yield rule

    def getStylesForElement(self,element:HtmlElementLike)->CssStyles:
        """
        Get the final style for this element.

        NOTE: does not yet include inherited ("cascaded") styles!
        """
        return CssStyles(self.getRulesForElement(element))
    getStyleForElement=getStylesForElement

    def condense(self,rename:bool=False)->typing.Dict[str,str]:
        """
        For all Rules that share the same set of css styles,
        will collaps them into one. Eg

            .style1 { color:red }
            .style2 { color:red }
        becomes
            .style1, .style2 { color:red }

        rename - an aggressive optomization that in the above example
            will delete .style2 and in the returned dict tell you it
            renamed{'.style2':'.style1'}
        """
        renamed:typing.Dict[str,str]={}
        # TODO: write the condensing routine
        return renamed

    def removeSelector(self,cssSelector:CssSelectorCompatible)->None:
        """
        remove one or more css selectors from the list
        """
        for rule in self._rules:
            if rule.hasSelector(cssSelector):
                rule.removeSelector(cssSelector)
                # if there are no selectors left, there is no rule
                if rule.numSelectors<1:
                    self._rules.remove(rule)
    remove=removeSelector

    def getStyles(self,
        nugg:cssTools.SearchNuggetCompatible
        )->typing.Optional[cssTools.CssStyles]:
        """
        collect all the styles that apply to a given element
        """
        nugg=cssTools.asSearchNugget(nugg)
        ret=None
        for rule in self._rules:
            style=rule.getStyles(nugg)
            if style is not None:
                if ret is None:
                    ret=cssTools.CssStyles(style)
                else:
                    ret.append(style)
        return ret

    def obfuscate(self,
        ignore:typing.Optional[CssSelectorsCompatible]=None
        )->typing.Dict[CssSelector,CssSelector]:
        """
        ignore is used to skip values that have already been used

        NOTE: for now, this is just a name swap, but could be made
        more sophisticated in various ways.

        returns {originalName:newName}
        """
        import random
        import re
        obfuscationKey:typing.Dict[CssSelector,CssSelector]={}
        if ignore is not None:
            # each "ignore" key simply obfuscates to itself
            ignore=CssSelectors(ignore)
            for s in ignore:
                obfuscationKey[s]=s
        used:typing.Set[str]=set()
        def obfuscateSelector(original:CssSelector)->CssSelector:
            """
            Takes a selector like
                "@myElement.element1" and transforms it into
                something unreadable like "@wM5a13.q1XjY"
            """
            def obfuscatedString()->str:
                """
                Gets a single obfuscated string we haven't used before.
                This leans toward creating shorter strings for efficiency.
                """
                buf=bytearray((random.randint(0x61,0x7a),))
                result=str(buf,encoding='ascii')
                while buf in used:
                    choice=random.randint(0,2)
                    if choice==0: # numeric digits
                        buf.append(random.randint(0x30,0x39))
                    elif choice==1: # capital letters
                        buf.append(random.randint(0x41,0x5a))
                    elif choice==1: # lowercase letters
                        buf.append(random.randint(0x61,0x7a))
                    result=str(buf,encoding='ascii')
                used.add(result)
                return result
            parts=re.finditer('([^a-zA-Z0-9]+)|([a-zA-Z0-9])',str(original))
            results:typing.List[str]=[]
            for m in parts:
                part=str(m.group(0))
                if part[0].isalpha():
                    results.append(obfuscatedString())
                else:
                    results.append(part)
            return CssSelector(''.join(results))
        # go through all the selectors and make sure they all
        # translate to the same values
        for rule in self._rules:
            for selector in rule.selectors:
                if selector not in obfuscationKey:
                    obfuscationKey[selector]=obfuscateSelector(selector)
                rule.removeSelector(selector)
                rule.addSelector(obfuscationKey[selector])
        return obfuscationKey
