"""
a handy, pythonic class wrapper around css
"""
import typing
from paths import UrlCompatible
from htmlTools import Text,Html
from .rules import CssRules,CssRulesCompatible,CssRule
from .htmlTypes import HtmlElementLike
from .cssStyles import CssStyles,CssStylesCompatible,asCssStyles
from .cssSelectors import CssSelectorCompatible


CssCompatible=CssRulesCompatible
def asCss(css:typing.Optional[CssCompatible])->'Css':
    """
    Always returns a Css object.
    if css is already a Css object,
        returns unchanged

    :param css: something to make into a Css
    :type css: CssCompatible
    :return: always a Css
    :rtype: Css
    """
    if isinstance(css,Css):
        return css
    return Css(data=css)


class Css(Text):
    """
    An entire css file (whether in its own file or embedded inside html)
    """

    def __init__(self,
        filename:typing.Optional[UrlCompatible]=None,
        data:typing.Optional[CssCompatible]=None):
        """ """
        Text.__init__(self,filename)
        if data is not None:
            self.assign(data)
        self.suggestions_separator='_'
        self.suggestions_firstchar='abcdefghijklmnopurstuvwxyz'
        self.suggestions_otherchars='123456789abcdefghijklmnopurstuvwxyz'
        self.rules:CssRules=CssRules()

    @typing.overload
    def __getitem__(self,idx:int
        )->CssRule:
        ...
    @typing.overload
    def __getitem__(self,idx:slice
        )->typing.Iterable[CssRule]:
        ...
    def __getitem__(self,
        idx:typing.Union[int,slice]
        )->typing.Union[CssRule,typing.Iterable[CssRule]]:
        return self.rules[idx]

    def getRuleForStyles(self,
        styles:CssStylesCompatible
        )->typing.Optional[CssRule]:
        """
        get a rule that matches a given styles set

        NOTE: will only return the first one it encounters,
        so depending on what you are doing, you may need to
        optimize first!
        """
        styles=asCssStyles(styles)
        for rule in self.rules:
            if rule.styles==styles:
                return rule
        return None

    def hasSelector(self,cssSelector:CssSelectorCompatible)->bool:
        """
        determine if the thing has a given css selector

        :param str: [description]
        :type str: [type]
        """
        return self.rules.hasSelector(cssSelector)

    def getRulesForElement(self,
        element:HtmlElementLike
        )->typing.Iterable[CssRule]:
        """
        get all rules that apply to a given element
        """
        return self.rules.getRulesForElement(element)
    getRules=getRulesForElement

    def getStyles(self,
        element:HtmlElementLike
        )->typing.Optional[CssStyles]:
        """
        create a combined style that collects all styles
        that apply to a given element
        """
        return self.rules.getStyles(element)
    getStyle=getStyles

    def assign(self, # type: ignore
        rule:CssRulesCompatible
        )->None:
        """
        Assign the value of the rules
        """
        self.rules.assign(rule)
    setCssRules=assign

    def addCssRules(self,
        rule:CssRulesCompatible
        )->None:
        """
        Add a new rule
        """
        self.rules.addCssRules(rule)
    addCssRule=addCssRules
    addRules=addCssRules
    addRule=addCssRules
    add=addCssRules
    append=addCssRules
    extend=addCssRules
    merge=addCssRules

    def __iter__(self)->typing.Iterator[CssRule]:
        return iter(self.rules)

    def getAvailableSelectorName(self,suggestion:str)->str:
        """
        Get a new selector based on a suggestion

        NOTE: if the suggestion is a tag-type selector and it has to change,
            will return a .class type selector.

        :param suggestion: if you don't have a name preference, you can send in '','@','.'
            to tell it what type
        :type suggestion: str
        :return: a new name
        :rtype: str
        """
        if suggestion=='':
            suggestion='.'
        elif suggestion[0] not in ('.','#'):
            if self.hasSelector(suggestion):
                suggestion='.'+suggestion
            else:
                return suggestion
        suggStack=[0,0,['*']] # column,columnidx,first_col_choices,subsequent_col_choices,current
        def nextSuggestion()->str:
            """
            get the next suggestion affix
            """
            if suggStack[0]==0:
                suggStack[2][suggStack[0]]=self.suggestions_firstchar[suggStack[1]]
                sugg=''.join(suggStack[2])
                suggStack[1]+=1
                if suggStack[1]>=len(self.suggestions_firstchar):
                    suggStack[0]+=1
                    suggStack[1]=0
                    suggStack[2].append('*')
            else:
                suggStack[4][suggStack[0]]=self.suggestions_otherchars[suggStack[1]]
                sugg=''.join(suggStack[2])
                suggStack[1]+=1
                if suggStack[1]>=len(self.suggestions_otherchars):
                    suggStack[0]+=1
                    suggStack[1]=0
                    suggStack[2].append('*')
            return sugg
        trySuggestion=suggestion
        while True:
            if not self.hasSelector(trySuggestion):
                return trySuggestion
            if suggestion in ('.','#'):
                trySuggestion=suggestion+nextSuggestion()
            else:
                trySuggestion=suggestion+self.suggestions_separator+nextSuggestion()

    def obfuscate(self,
        ignore:typing.Optional[typing.Iterable[str]]=None
        )->typing.Dict[str,str]:
        """
        ignore is used to skip values that have already been used

        returns {originalName:newName}
        """
        remapped={}
        if ignore is not None:
            for name in ignore:
                remapped[name]=name
        for rule in self:
            remapped.update(rule.obfuscate(remapped))
        return remapped

    def applyCssTranslations(self,
        translations:typing.Dict[str,str],
        toHtml:Html
        )->None:
        """
        functions like self.obfuscate() and self.merge() may return translation
        tables for renaming css rules.  This is used to then apply those
        rules to html.

        NOTE: does not yet support multiple classes eg
            <tag class="this,that"/>

        :param typing: [description]
        :type typing: [type]
        :param toHtml: [description]
        :type toHtml: Html
        """
        for el in toHtml.walkElements():
            translation=translations.get(el.tagName)
            if translation is None:
                if 'id' in el.attrib:
                    translation=translations.get('@'+el.attrib['id'])
                if translation is None and 'class' in el.attrib:
                    for cssClass in el.attrib['class'].split():
                        cssClass=cssClass.strip()
                        translation=translations.get('.'+cssClass)
            if translation is not None:
                if translation[0]=='@':
                    el.attrib['id']=translation[1:]
                elif translation[0]=='.':
                    el.attrib['class']=translation[1:]
                else:
                    el.tagName=translation

    def getCssString(self,indent='\t',prepend='\n'):
        """
        Returns the css text
        """
        return self.rules.getCssString(indent,prepend)
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
