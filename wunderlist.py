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


ListItemType=typing.TypeVar("ListItemType",NamedObject,NamedObject)
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

    def __iter__(self)->typing.Iterator[ListItemType]:
        for item in self._items.values():
            yield item

    def __len__(self)->int:
        return len(self._items)

    def __getitem__(self,
        idx:typing.Union[int,slice,str]
        )->ListItemType:
        result=self.get(idx,IndexError)
        if result is IndexError:
            raise result()
        return result

    @typing.overload
    def get(self,
        idx:typing.Union[int,slice,str],
        default:ListItemCompatibleType
        )->ListItemCompatibleType:
        ...
    @typing.overload
    def get(self,
        idx:typing.Union[int,slice,str],
        default:typing.Any=None
        )->typing.Any:
        ...
    def get(self,
        idx:typing.Union[int,slice,str],
        default:typing.Any=None
        )->typing.Any:
        """
        if default=IndexError, will raise that when not found
        """
        if isinstance(idx,str):
            return self._items.get(idx,default)
        try:
            return list(self._items.values())[idx]
        except IndexError as e:
            if default==IndexError:
                raise e
        return default

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
            for item in self._decode(items):
                self._items[item.name]=item
        elif isinstance(items,ListItemType):
            self._items[items.name]=items
        elif isinstance(items,ListItemCompatibleType):
            items=ListItemType(items)
            self._items[items.name]=items # pylint: disable=no-member
        else:
            for item in items:
                self.append(item)

    @abstractmethod
    def _decode(self,data:str)->typing.Iterable[ListItemType]:
        """
        decode a string into this data type

        :param data: data to decode
        """
        for item in data.split(','):
            yield ListItemType(item.strip())

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
