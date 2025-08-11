
"""
A single formatting rule

A rule consists of a series of selectors and
a series of CssStyles that they all map to
"""
import typing
import cssTools


class CssRule:
    """
    A single formatting rule

    A rule consists of a series of selectors and
    a series of CssStyles that they all map to
    """

    def __init__(self,
        selectors:typing.Iterable[str],
        styles:cssTools.CssStylesCompatible):
        """ """
        self._selectors:typing.Set[str]=set(selectors)
        self._styles:cssTools.CssStyles=cssTools.CssStyles(styles)

    def hasSelector(self,selector:typing.Optional[str])->bool:
        """
        See if the given selector is present in the set of selectors

        :param selector: [description]
        :type selector: str
        :return: [description]
        :rtype: bool
        """
        if selector is None:
            return False
        return selector in self._selectors

    def sameStyles(self,otherStyles:cssTools.CssStyles)->bool:
        """
        Determine if the set of styles is the same as another
        set of styles.
        (Useful for things like reducing duplicates)
        """
        return otherStyles==self._styles

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

    def obfuscate(self,ignore:typing.Dict=None)->typing.Dict[str,str]:
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

    def condense(self,rename=None)->typing.Dict[str,str]:
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

    def remove(self,cssSelector:str)->None:
        """
        remove one or more css selectors from the list
        """

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

    def obfuscate(self,ignore:typing.Dict=None)->typing.Dict[str,str]:
        """
        ignore is used to skip values that have already been used

        returns {originalName:newName}
        """
