"""
Database API
"""
from typing import Union
from abc import ABC, abstractmethod


BytesOrNone = Union[bytes, None]


class TreeMapStore(ABC):
    @abstractmethod
    def get_value(self, key: bytes) -> BytesOrNone:
        """
        Get a leaf value for the given key.
        Returns:
            - Value if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def get_node(self, key: bytes) -> BytesOrNone:
        """
        Get a node for the given key.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def set_value(self, key: bytes, value: bytes) -> bool:
        """
        Put a leaf key,value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def set_node(self, key: bytes, value: bytes) -> bool:
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def delete_value(self, key) -> bool:
        """
        Delete a leaf value
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def delete_node(self, key) -> bool:
        """
        Delete a node
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass


class TreeMemoryStore(TreeMapStore):
    nodes: dict
    values: dict

    def __init__(self):
        self.nodes = {}
        self.values = {}

    def get_value(self, key: bytes) -> BytesOrNone:
        """
        Get a leaf value for the given key.
        Returns:
            - Value if the key exists, or
            - None if it's not found
        """
        return self.values.get(key, None)

    def get_node(self, key: bytes) -> BytesOrNone:
        """
        Get a node for the given key.
        Returns:
            - Node if the key exists, or
            - None if it's not found
        """
        return self.nodes.get(key, None)

    def set_value(self, key: bytes, value: bytes) -> bool:
        """
        Put a leaf key,value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        self.values[key] = value
        return True

    def set_node(self, key: bytes, value: bytes) -> bool:
        """
        Put a node value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        self.nodes[key] = value
        return True

    def delete_value(self, key) -> bool:
        """
        Delete a leaf value
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        if key not in self.values:
            return False
        del self.values[key]
        return True

    def delete_node(self, key) -> bool:
        """
        Delete a node
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        if key not in self.nodes:
            return False
        del self.nodes[key]
        return True
