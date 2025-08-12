"""
Stubs and types for html

Can support lxml and/or htmltools if installed
"""
import typing
import xml.dom.minidom
MinidomElement=xml.dom.minidom.Element
try:
    import lxml.etree
    LxmlElement=lxml.etree.Element
except ImportError:
    LxmlElement=MinidomElement
try:
    from htmlTools import HtmlCompatible
except ImportError:
    HtmlCompatible=MinidomElement

HtmlElementLike=typing.Union[LxmlElement,MinidomElement]
HtmlElementsLike=typing.Union[HtmlElementLike,typing.Iterable[HtmlElementLike],HtmlCompatible]
