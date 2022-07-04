"""
Database API
"""

from abc import ABC, abstractmethod
from typing import Union

BytesOrNone = Union[bytes, None]


class TreeMapNodes(ABC):
    @abstractmethod
    def __getitem__(self, key: bytes) -> BytesOrNone:
        """
        :param key: path to node
        :return: node if the key exists, or `None` if not found
        """

        pass

    @abstractmethod
    def __setitem__(self, key: bytes, value: bytes):
        """
        Put a node in the store, overwriting an existing path.

        :param key: path to node
        :param value: value to place within tree
        """

        pass

    @abstractmethod
    def __delitem__(self, key: bytes) -> bool:
        pass


class TreeMapStore(ABC):
    nodes: TreeMapNodes

    @abstractmethod
    def __getitem__(self, key: bytes) -> BytesOrNone:
        """
        :param key: path to node
        :return: leaf value if the key exists, or `None` if not found
        """

        pass

    @abstractmethod
    def __setitem__(self, key: bytes, value: bytes):
        """
        Put a key-value pair in the store as a leaf node, overwriting an existing path.

        :param key: path to node
        :param value: value to place within tree
        """

        pass

    @abstractmethod
    def __delitem__(self, key: bytes) -> bool:
        pass


class TreeMemoryNodes(TreeMapNodes):
    nodes = dict

    def __init__(self):
        self.nodes = {}

    def __getitem__(self, key: bytes) -> BytesOrNone:
        return self.nodes.get(key, None)

    def __setitem__(self, key: bytes, value: bytes):
        self.nodes[key] = value

    def __delitem__(self, key: bytes):
        if key not in self.nodes:
            raise KeyError(f"path {key} not in tree")
        del self.nodes[key]


class TreeMemoryStore(TreeMapStore):
    nodes: TreeMemoryNodes
    values: dict

    def __init__(self):
        self.nodes = TreeMemoryNodes()
        self.values = {}

    def __getitem__(self, key: bytes) -> BytesOrNone:
        return self.values.get(key, None)

    def __setitem__(self, key: bytes, value: bytes):
        self.values[key] = value

    def __delitem__(self, key: bytes):
        if key not in self.values:
            raise KeyError(f"path {key} not in tree")
        del self.values[key]
