"""
a handy, pythonic class wrapper around css
"""
import typing
from htmlTools import HtmlAndText,Html
import cssTools


CssCompatible=typing.Union['Css',str]
def asCss(css:CssCompatible)->'Css':
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
    return Css(css)


class Css(HtmlAndText):
    """
    An entire css file (whether in its own file or embedded inside html)
    """

    def __init__(self,filename=None,data=None):
        HtmlAndText.__init__(self,filename,data)
        self.suggestions_separator='_'
        self.suggestions_firstchar='abcdefghijklmnopurstuvwxyz'
        self.suggestions_otherchars='123456789abcdefghijklmnopurstuvwxyz'
        self.rules:typing.List[cssTools.CssRule]

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self,
        idx:typing.Union[int,typing.Tuple[int,int],cssTools.SearchNuggetCompatible]
        )->typing.Union[None,cssTools.CssRule,cssTools.CssStyles]:
        """
        [] operator can take an int or slice, which works
        on self.rules, or it can take a SearchNuggetCompatible,
        which performs a getStyles() search.
        Thus, css[".classname"] returns a Styles object for that css classname
        """
        if isinstance(idx,(int,tuple)):
            return self.rules[idx]
        return self.getStyles(idx)

    def getRuleForStyles(self,
        styles:cssTools.CssStylesCompatible
        )->typing.Optional[cssTools.CssRule]:
        """
        get a rule that matches a given styles set

        NOTE: will only return the first one it encounters,
        so depending on what you are doing, you may need to
        optimize first!
        """
        styles=cssTools.asCssStyles(styles)
        for rule in self.rules:
            if rule.styles==styles:
                return rule
        return None

    def hasSelector(self,cssSelector:str)->bool:
        """
        determine if the thing has a given css selector

        :param str: [description]
        :type str: [type]
        """
        if self.getRule(cssSelector):
            return True
        return False

    def getRule(self,
        nugg:cssTools.SearchNuggetCompatible
        )->typing.Optional[cssTools.CssRule]:
        """
        collect all the styles that apply to a given element
        """
        nugg=cssTools.asSearchNugget(nugg)
        for rule in self.rules:
            if rule.matches(nugg):
                return rule
        return None

    def getStyles(self,
        nugg:cssTools.SearchNuggetCompatible
        )->typing.Optional[cssTools.CssStyles]:
        """
        collect all the styles that apply to a given element
        """
        nugg=cssTools.asSearchNugget(nugg)
        ret=None
        for rule in self.rules:
            styles=rule.getStyles(nugg)
            if ret is None:
                ret=styles
            else:
                ret.append(styles)
        return ret

    def addRule(self,rule:cssTools.CssRule)->typing.Dict[str,str]:
        """
        returns a new name if the rule had to be renamed to fit

        :param rule: rule to add
        :type rule: Rule
        :return: returns any values that had to be renamed
        :rtype: dict
        """
        ret:typing.Dict[str,str]={}
        for selector in rule.selectors:
            # Rules have more than one selector!
            ourRule=self.getRule(selector)
            if ourRule is None:
                # we don't have anything like that
                ourRule=self.getRuleForStyles(rule.styles)
                if ourRule is None:
                    # add a new rule with just this one selector
                    newRule=cssTools.CssRule(selector,rule.styles)
                    self.rules.append(newRule)
                else:
                    ourRule.selectors.add(selector)
            elif ourRule.styles==rule.styles:
                # nothing to do.  it's exactly the same thing.
                self.rules.append(rule)
            else:
                # it's a rule of the same name with different styles
                # so we have to rename
                newName=self.getAvailableSelectorName(selector)
                if newName!=selector:
                    ret[selector]=newName
                newRule=cssTools.CssRule(newName,rule.styles)
                self.rules.append(newRule)
        return ret

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

    def merge(self,otherCss:CssCompatible)->typing.Dict[str,str]:
        """
        IMPORTANT: for items that collide, returns a mapping to new names.
            These entities should be located and renamed before merging html documents.
        """
        remapped={}
        otherCss=asCss(otherCss)
        for rule in otherCss:
            remapped.update(self.addRule(rule))
        return remapped

    def obfuscate(self,ignore:typing.Dict=None)->typing.Dict[str,str]:
        """
        ignore is used to skip values that have already been used

        returns {originalName:newName}
        """
        remapped=dict(ignore)
        for rule in self:
            remapped.update(rule.obfuscate(remapped))
        return remapped

    def applyCssTranslations(self,translations:typing.Dict[str,str],toHtml:Html)->None:
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

    def _parseCssRules(self,dom):
        """
        DEPRECATED

        Returns an dictionary of rule:css for the given document
        Note that items on the same line "a, .class {foo}" will each get their own entry.
        """
        rules={}
        elements=dom.getElementsByTagName("style")
        for element in elements:
            css=''
            for node in element.childNodes:
                if node.nodeType!=node.ATTRIBUTE_NODE:
                    css=css+node.toxml()
            css=css.split('}') # split into lines of css
            for cssLine in css:
                cssLine=cssLine.split('{')
                if len(cssLine)!=2:
                    continue
                rule=cssLine[1].strip()
                cssLine=cssLine[0].split(',')
                for ruleName in cssLine:
                    ruleName=ruleName.strip()
                    self.addCssRules(rules,{ruleName:rule},True)
        return rules

    def getCssString(self,rules,indent='\t',prepend='\n'):
        """
        DEPRECATED

        Takes a dictionary of rule:css and returns the (collapsed) css text
        """
        sdrawkcab={}
        for k,v in list(rules.items()):
            if v in sdrawkcab:
                sdrawkcab[v]=sdrawkcab[v]+', '+k
            else:
                sdrawkcab[v]=k
        out=prepend
        for v,k in list(sdrawkcab.items()):
            out=out+indent+k+' {'+v+'}\n'
        return out

    def addCssRules(self,addTo,add,combineRules=True,overwrite=False,removeMissing=False):
        """
        DEPRECATED

        Adds the 'add' set of rules to the 'addTo' set

        combineRules (used when overwrite=False) to combine the new css formatting with the old
        overwrite makes the new rule obliterate the old rule completely
        removeMissing is used to remove all rules from addTo which are not found in add

        Examples: addTo= "a {border:raised}" add="a {border:none;font:times}"
                if combineRules=N/A,overwrite=True "a {border:none;font:times}"
                if combineRules=True,overwrite=False "a {border:raised;font:times}"
                if combineRules=False,overwrite=False "a {border:raised}"
        """
        for k,v in list(add.items()):
            if overwrite or k not in addTo:
                addTo[k]=v
            elif combineRules:
                rulesAddTo={}
                for rule in addTo[k].split(';'):
                    rule=rule.split(':',1)
                    rulesAddTo[rule[0].strip()]=rule[1].strip()
                for rule in v.split(';'):
                    rule=rule.split(':',1)
                    if rule[0].strip() not in rulesAddTo:
                        rulesAddTo[rule[0].strip()]=rule[1].strip()
                v=''
                first=True
                for ruleName,rule in list(rulesAddTo.items()):
                    if first:
                        v=ruleName+':'+rule
                        first=False
                    else:
                        v=v+';'+ruleName+':'+rule
        if removeMissing:
            for k,v in list(addTo.items()):
                if k not in add:
                    del addTo[k]

    def setCssRules(self,dom,cssNewRules,combineRules=True,overwrite=False,removeMissing=False):
        """
        DEPRECATED

        Sets the css of the given document to the given set of rules.

        Examples: existing= "a {border:raised}" cssNewRule="a {border:none;font:times}"
                if combineRules=N/A,overwrite=True "a {border:none;font:times}"
                if combineRules=True,overwrite=False "a {border:raised;font:times}"
                if combineRules=False,overwrite=False "a {border:raised}"

        Returns the entire combined set of rules.

        NOTE: Will create html parent tags as necessary.
        """
        # make <html><head><style> exist.
        elements=dom.getElementsByTagName('style')
        if elements is None or len(elements)==0:
            new=dom.createElement('style')
            new.setAttribute('type','text/css')
            headTag=dom.getElementsByTagName('head')
            if headTag is None or len(headTag)==0:
                headTag=dom.createElement('head')
                htmlTag=dom.getElementsByTagName('html')[0]
                htmlTag.appendChild(headTag)
            else:
                headTag=headTag[0]
            headTag.appendChild(new)
            elements=dom.getElementsByTagName('style')
        # Merge with the current rules
        rules=self.extractCssRules(dom)
        self.addCssRules(rules,cssNewRules,combineRules,overwrite,removeMissing)
        # Set the merged set into the document
        first=True
        for element in elements:
            if first:
                first=False
                # out with the old
                while element.firstChild is not None:
                    element.removeChild(element.firstChild)
                # in with the new
                css=dom.createTextNode(self.getCssString(rules))
                element.appendChild(css)
            else:
                # should only be one, so delete any others
                element.parent.removeChild(element)
        # Returns the merged list in case they need it
        return rules

    def createMissingCSS(self,dom,cssDefaultRules):
        """
        DEPRECATED

        Adds the {name:rule} dictionary of css rules to the given
        dom document if they are missing.

        Will create html parent tags as necessary.
        """
        self.setCssRules(dom,cssDefaultRules,False,False)