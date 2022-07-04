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
    def __setitem__(self, key: bytes, value: bytes) -> bool:
        """
        Put a node in the store, overwriting an existing path.

        :param key: path to node
        :param value: value to place within tree
        :return: whether operation was successful
        """

        pass

    @abstractmethod
    def delete(self, key: bytes) -> bool:
        """
        :return: whether delete was successful
        """

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
    def __setitem__(self, key: bytes, value: bytes) -> bool:
        """
        Put a key-value pair in the store as a leaf node, overwriting an existing path.

        :param key: path to node
        :param value: value to place within tree
        :return: whether operation was successful
        """

        pass

    @abstractmethod
    def delete(self, key: bytes) -> bool:
        """
        :return: whether delete was successful
        """

        pass


class TreeMemoryNodes(TreeMapNodes):
    nodes = dict

    def __init__(self):
        self.nodes = {}

    def __getitem__(self, key: bytes) -> BytesOrNone:
        return self.nodes.get(key, None)

    def __setitem__(self, key: bytes, value: bytes) -> bool:
        self.nodes[key] = value
        return True

    def delete(self, key: bytes) -> bool:
        if key not in self.nodes:
            return False
        del self.nodes[key]
        return True


class TreeMemoryStore(TreeMapStore):
    nodes: TreeMemoryNodes
    values: dict

    def __init__(self):
        self.nodes = TreeMemoryNodes()
        self.values = {}

    def __getitem__(self, key: bytes) -> BytesOrNone:
        return self.values.get(key, None)

    def __setitem__(self, key: bytes, value: bytes) -> bool:
        self.values[key] = value
        return True

    def delete(self, key: bytes) -> bool:
        if key not in self.values:
            return False
        del self.values[key]
        return True
