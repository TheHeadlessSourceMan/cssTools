"""
Stubs and types for html

Can support lxml and/or htmltools if installed
"""
import typing
import xml.dom.minidom
MinidomElement=xml.dom.minidom.Element
try:
    from lxml.etree import _Element as LxmlElement  # pyright: ignore[reportPrivateUsage]
except ImportError:
    class LxmlElement(MinidomElement):
        """Placeholder so the name is always a real class."""
try:
    from htmlTools import HtmlCompatible
except ImportError:
    class HtmlCompatible(MinidomElement):
        """Placeholder so the name is always a real class."""

HtmlElementLike=typing.Union[LxmlElement,MinidomElement]
HtmlElementsLike=typing.Union[
    HtmlElementLike,
    typing.Iterable[HtmlElementLike],
    HtmlCompatible]
