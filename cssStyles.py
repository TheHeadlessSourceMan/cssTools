"""
Manages Css styles

CssStyles can be accessed like a dict of name:value
"""
import typing
import cssTools


CssStylesCompatible=typing.Union['CssStyles',str,
    typing.Iterable[typing.Union['CssStylesCompatible']]]
def asCssStyles(styles:CssStylesCompatible)->'CssStyles':
    """
    Always returns a CssStyles object.
    if styles is already a CssStyles object,
        returns unchanged

    :param styles: something to make into a CssStyles
    :type styles: CssStylesCompatible
    :return: always a CssStyles
    :rtype: CssStyles
    """
    if isinstance(styles,CssStyles):
        return styles
    return CssStyles(styles)


class CssStyles(cssTools.Wunderlist['CssStyles',CssStylesCompatible]):
    """
    Manages Css styles

    CssStyles can be accessed like a dict of name:value
    """

    def __init__(self,styles:typing.Optional[CssStylesCompatible]=None):
        cssTools.Wunderlist.__init__(self,styles)
        if styles is not None:
            self.assign(styles)

    def combined(self,other:CssStylesCompatible)->"CssStyles":
        """
        Get this style combined with some other.
        """
        return CssStyles((self,other))

    def __add__(self,other:CssStylesCompatible)->"CssStyles":
        return CssStyles((self,other))

    def __eq__(self, # type: ignore
        otherStyles:CssStylesCompatible)->bool:
        return self.sameStyles(otherStyles)
    def sameStyles(self,otherStyles:CssStylesCompatible)->bool:
        """
        Determine if the set of styles is the same as another
        set of styles.
        (Useful for things like reducing duplicates)
        """
        otherStyles=asCssStyles(otherStyles)
        if len(self._items)!=len(otherStyles):
            return False
        for item in self:
            if item not in otherStyles:
                return False
        return True

    def appendCssString(self,data:str)->None:
        """
        decode from css string
        """
        data=data.strip()
        if data[0]=='{':
            data=data[1:-1].strip()
        for styleItem in data.split(';'):
            nameval=[nv.strip() for nv in styleItem.split(':',1)]
            if len(nameval)>1:
                self._items[nameval[0]]=nameval[1]

    @property
    def styleAttribute(self)->str:
        """
        these rules as a style="" html attribute
        """
        return 'style="%s"'%self.styleAttributeContents

    @property
    def styleAttributeContents(self)->str:
        """
        given a style="" attribute, just the stuff in quotes
        """
        kvset=['%s:%s'%kv for kv in self._items.items()]
        return ';'.join(kvset)

    @property
    def cssFileFormat(self)->str:
        """
        css of the form:
        {
            width:120px;
            color:red;
            ...
        }
        """
        return self.getCssFileFormat()

    def getCssFileFormat(self,indent='',indenter='\t',newline='\n',curlies=True)->str:
        """
        returns css of the form:
        {
            width:120px;
            color:red;
            ...
        }
        """
        ret:typing.List[str]=[]
        if curlies:
            ret=[indent+'{']
        for kv in self._items.items():
            ret.append(f'{indent}{indenter}{kv[0]}: {kv[1]};')
        if curlies:
            ret.append(indent+'}')
        return newline.join(ret)

    def __repr__(self,indent='',indenter='\t')->str:
        return self.getCssFileFormat(indent,indenter)
    def __str__(self,indent='',indenter='\t')->str:
        return self.getCssFileFormat(indent,indenter)

    def getCssString(self,indent='\t',prepend='\n'):
        """
        Returns the css text
        """
        return self.getCssFileFormat(indenter=indent,newline=prepend)
    def setCssString(self,cssString:str)->None:
        """
        Assigns the css text
        """
        self.assign(cssString)

    @property
    def cssString(self)->str:
        """
        This object as a css string
        """
        return self.getCssString('','')
    @cssString.setter
    def cssString(self,cssString:str):
        self.setCssString(cssString)\

CssStyle=CssStyles
