"""
Stubs and types for html
"""
import typing
import xml.dom.minidom
import lxml.etree


HtmlElementLike=typing.Union[lxml.etree.Element,xml.dom.minidom.Element]
HtmlElementsLike=typing.Union[HtmlElementLike,typing.Iterable[HtmlElementLike]]
