"""
Database API
"""
from abc import ABC, abstractmethod
from typing import Union


BytesOrNone = Union[bytes, None]


class DatabaseAPI(ABC):
    """
    Basic 'interface' expected by the SparseMerkle Tree for storage
    """

    @abstractmethod
    def get(self, key: bytes) -> BytesOrNone:
        """
        Get a value for the given key.
        Returns:
            - Value if the key exists, or
            - None if it's not found
        """
        pass

    @abstractmethod
    def put(self, key: bytes, value: bytes) -> bool:
        """
        Put a key,value in the store. Overwrite the value for existing keys.
        Returns:
            - True if the write succeeds
            - False if it doesn't
        """
        pass

    @abstractmethod
    def delete(self, key) -> bool:
        """
        Delete a key/value pair
         Returns:
            - True if the delete succeeds
            - False if it doesn't
        """
        pass


class MemoryStore(DatabaseAPI):
    """
    In-memory implementation
    """

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def put(self, key, value):
        self.store[key] = value
        return True

    def delete(self, key) -> bool:
        if key not in self.store:
            return False
        del self.store[key]
        return True
