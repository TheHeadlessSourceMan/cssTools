"""
A single formatting rule

A rule consists of a series of selectors and
a series of CssStyles that they all map to
"""
import typing
import re
from htmlTypes import HtmlElementLike
from .cssStyles import CssStyles,CssStylesCompatible
from .cssSelectors import CssSelector,CssSelectors,CssSelectorsCompatible,CssSelectorCompatible
if typing.TYPE_CHECKING:
    from .css import Css

CssRuleCompatible=typing.Union[str,'CssRule']
CssRulesCompatible=typing.Union[
    CssRuleCompatible,'CssRules','Css',typing.Iterable['CssRuleCompatible']]


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
        other:typing.Union[None,str,"CssRule"]
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

    def matches(self,element:HtmlElementLike)->bool:
        """
        Determine if this rule applies to the given selection
        :rtype: bool
        """
        return self.selectors.matches(element)

    def getStyles(self,
        element:HtmlElementLike
        )->typing.Optional[CssStyles]:
        """
        collect all the styles that apply to a given element
        """
        if self.matches(element):
            return self.styles
        return CssStyles()
    getStyle=getStyles

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

    def getCssString(self,indent='\t',prepend='\n'):
        """
        Returns the css text
        """
        ret:typing.List[str]=[]
        for selector in self.selectors:
            ret.append(str(selector))
        ret=[', '.join(ret),' {']
        ret.append(self.styles.getCssString(indent,prepend))
        ret.append(prepend)
        ret.append('}')
        return ''.join(ret)
    #setCssString=assign

    @property
    def cssString(self)->str:
        """
        This object as a css string
        """
        return self.getCssString()
    #@cssString.setter
    #def cssString(self,cssString:str):
    #    self.setCssString(cssString)

    def __repr__(self)->str:
        return self.getCssString()
Rule=CssRule


class CssRules:
    """
    A set of formatting rules.
    """

    RULES_SPLITTER_RE=re.compile(
        r"""(?P<selectors>[.@:a-z][^{]*)\{(?P<styles>[^}]*)\}""",re.IGNORECASE|re.DOTALL)

    def __init__(self,rules:typing.Optional[CssRulesCompatible]=None):
        self._rules:typing.List[CssRule]=[]
        if rules is not None:
            self.addCssRules(rules)

    def __iter__(self)->typing.Iterator[CssRule]:
        return iter(self._rules)

    @typing.overload
    def __getitem__(self,idx:int
        )->CssRule:
        ...
    @typing.overload
    def __getitem__(self,idx:slice
        )->typing.Iterable[CssRule]:
        ...
    def __getitem__(self,idx:typing.Union[int,slice]
        )->typing.Union[CssRule,typing.Iterable[CssRule]]:
        return self._rules[idx]

    def __len__(self)->int:
        return len(self._rules)

    def clear(self):
        """
        clear out all rules
        """
        self._rules.clear()

    def assign(self,rules:CssRulesCompatible)->None:
        """
        Assign this object to a set of rules
        """
        self.clear()
        self.addCssRules(rules)

    def addCssRules(self,rules:CssRulesCompatible)->None:
        """
        Add one or more rules
        """
        if isinstance(rules,str):
            for m in self.RULES_SPLITTER_RE.finditer(rules):
                rule=CssRule(m.group('selectors'),m.group('styles'))
                self._rules.append(rule)
        elif isinstance(rules,CssRule):
            self._rules.append(rules)
        elif isinstance(rules,CssRules):
            self._rules.extend(rules)
        else:
            for rule in rules:
                self.addCssRule(rule)
    addCssRule=addCssRules
    addRules=addCssRules
    addRule=addCssRules
    add=addCssRules
    append=addCssRules
    extend=addCssRules

    def getRulesForElement(self,element:HtmlElementLike)->typing.Iterable[CssRule]:
        """
        get all rules that apply to a given element
        """
        for rule in self._rules:
            if rule.matches(element):
                yield rule
    getRules=getRulesForElement

    def getStylesForElement(self,element:HtmlElementLike)->CssStyles:
        """
        Get the final style for this element.

        NOTE: does not yet include inherited ("cascaded") styles!
        """
        return CssStyles(self.getRulesForElement(element))
    getStyleForElement=getStylesForElement

    def hasSelector(self,cssSelector:CssSelectorCompatible)->bool:
        """
        determine if the thing has a given css selector

        :param str: [description]
        :type str: [type]
        """
        for rule in self._rules:
            if rule.hasSelector(cssSelector):
                return True
        return False

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
        _=rename
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
        element:HtmlElementLike
        )->typing.Optional[CssStyles]:
        """
        collect all the styles that apply to a given element
        """
        styleList:typing.List[CssStyles]=[]
        for rule in self._rules:
            style=rule.getStyles(element)
            if style is not None:
                styleList.append(style)
        return CssStyles(styleList)
    getStyle=getStyles

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

    def getCssString(self,indent='\t',prepend='\n'):
        """
        Returns the css text
        """
        ret:typing.List[str]=[]
        for rule in self._rules:
            ret.append(rule.getCssString(indent,prepend))
        return ('\n'+prepend).join(ret)
    setCssString=assign

    @property
    def cssString(self)->str:
        """
        This object as a css string
        """
        return self.getCssString()
    @cssString.setter
    def cssString(self,cssString:str):
        self.setCssString(cssString)

    def __repr__(self)->str:
        return self.getCssString()
Rules=CssRules
