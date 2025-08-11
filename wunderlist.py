"""
Creates a dict-like/list-like object of named values
"""
import typing
from abc import abstractmethod
from collections import OrderedDict


class NamedObject(typing.Protocol):
    """
    an object with a name.  duh.
    """
    name:str


ListItemType=typing.TypeVar("ListItemType",NamedObject)
ListItemCompatibleType=typing.TypeVar("ListItemCompatibleType")

class Wunderlist(typing.Generic[ListItemType,ListItemCompatibleType]):
    """
    Creates a dict-like/list-like object of named values
    """
    def __init__(self,
        items:typing.Union[
            None,str,ListItemCompatibleType,
            typing.Iterable[ListItemCompatibleType]]=None):
        """ """
        self._items:typing.Dict[str,ListItemType]=OrderedDict()
        if items is not None:
            self.assign(items)

    def __iter__(self):
        return self._items.values()

    def __getitem__(self,
        idx:typing.Union[int,typing.Tuple[int,int],str]
        )->ListItemType:
        return self.get(idx,IndexError)

    def get(self,
        idx:typing.Union[int,typing.Tuple[int,int],str],
        default:typing.Optional[ListItemCompatibleType]=None
        )->typing.Optional[ListItemCompatibleType]:
        """
        if default=IndexError, will raise that when not found
        """
        if isinstance(idx,str):
            val=self._items.get(idx,default)
        else:
            vv=self._items.values()
            if idx<0 or idx>len(vv):
                val=default
            else:
                val=vv[idx]
        if val==IndexError:
            raise IndexError()
        return val

    def update(self,
        items:typing.Union[None,str,ListItemCompatibleType,typing.Iterable[ListItemCompatibleType]]
        )->None:
        """
        same as append
        """
        self.append(items)
    def extend(self,
        items:typing.Union[None,str,ListItemCompatibleType,typing.Iterable[ListItemCompatibleType]]
        )->None:
        """
        same as append
        """
        self.append(items)
    def append(self,
        items:typing.Union[None,str,ListItemCompatibleType,typing.Iterable[ListItemCompatibleType]]
        )->None:
        """
        Add one or more items to this list
        """
        if items is None:
            return
        if isinstance(items,str):
            self._decode(str)
        elif isinstance(items,ListItemCompatibleType):
            items=ListItemType(items)
            self._items[items.name]=items # pylint: disable=no-member
        else:
            for item in items:
                item=ListItemType(item)
                self._items[item.name]=item # pylint: disable=no-member

    @abstractmethod
    def _decode(self,data:str)->None:
        """
        decode a string into this data type

        :param data: data to decode
        :type data: str
        """

    def assign(self,
        items:typing.Union[None,str,ListItemCompatibleType,typing.Iterable[ListItemCompatibleType]]
        )->None:
        """
        Assign this list to new values
        """
        self.clear()
        self.append(items)

    def clear(self):
        """
        clear out these items
        """
        self._items=OrderedDict()
