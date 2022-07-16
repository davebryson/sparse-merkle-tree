"""
Sparse Merkle Tree.
A Python port of: https://github.com/celestiaorg/smt
"""

from typing import Dict, List, Mapping, Sequence, Tuple

from .proof import SparseMerkleProof
from .store import BytesOrNone, TreeMapStore, TreeMemoryStore
from .utils import (
    DEFAULTVALUE,
    DEPTH,
    PLACEHOLDER,
    RIGHT,
    count_common_prefix,
    create_leaf,
    create_node,
    digest,
    get_bit,
    is_leaf,
    parse_leaf,
    parse_node,
)

# Errors
KeyAlreadyEmpty = 1
InvalidKey = 2


class SparseMerkleTree:
    root: bytes
    store: TreeMapStore

    def __init__(self, store: TreeMapStore = None, root: bytes = None):
        if store is None:
            store = TreeMemoryStore()
        if root is None:
            root = PLACEHOLDER

        self.root = root
        self.store = store

    @classmethod
    def from_data(
        cls,
        data: Dict[bytes, bytes],
        store: TreeMapStore = None,
        root: bytes = None,
    ) -> "SparseMerkleTree":
        tree = cls(store, root)

        for key, value in data.items():
            tree[key] = value

        return tree

    def __getitem__(self, key: bytes) -> bytes:
        """
        :param key: key within the tree
        :return: value at key (or empty bytes if key does not exist)
        """

        if self.root == PLACEHOLDER:
            return DEFAULTVALUE

        path = digest(key)
        val = self.store[path]
        if not val:
            return DEFAULTVALUE

        return val

    def __contains__(self, key: bytes) -> bool:
        return self[key] != DEFAULTVALUE

    def __setitem__(self, key: bytes, value: bytes):
        self.set(key, value)

    def set(self, key: bytes, value: bytes, root: bytes = None) -> BytesOrNone:
        """
        :param key: path to node to update
        :param value: value to place within tree
        :param root: path to node to apply to
        :return: new root path
        """

        tree_root = root is None

        if tree_root:
            root = self.root

        path = digest(key)
        side_nodes, path_nodes, old_leaf_data, _sibling_data = self._side_nodes(path, root)

        # If the value is the None (defaultValue) then do a delete for the key
        if value == DEFAULTVALUE:
            new_root, err = self._delete_with_side_nodes(path, side_nodes, path_nodes, old_leaf_data)

            if err is not None and err == KeyAlreadyEmpty:
                return root
            try:
                del self.store[path]
            except KeyError:
                return None
        else:
            new_root = self._update_with_side_nodes(path, value, side_nodes, path_nodes, old_leaf_data)

        if tree_root:
            self.root = new_root

        return new_root

    def __delitem__(self, key: bytes):
        self.delete(key)

    def delete(self, key: bytes, root: bytes = None) -> bytes:
        """
        :param key: path to node to delete
        :param root: path to node to apply to
        :return: new root path
        """

        return self.set(key, DEFAULTVALUE, root)

    def prove(self, key: bytes, root: bytes = None, updatable: bool = False) -> SparseMerkleProof:
        return self._proof(key, root, is_updatable=updatable)

    def __eq__(self, other: Mapping) -> bool:
        for key, value in other.items():
            if self[key] != value:
                return False
        else:
            return True

    def _side_nodes(
        self, path: bytes, root: bytes = None, with_sibling_data: bool = False
    ) -> Tuple[List[bytes], List[bytes], bytes, bytes]:
        """
        Walk the tree down from the root for the given key (path),
        gathering neighbor nodes on the way to the leaf.

        :param path: path to the node to walk
        :param root: node to apply to
        :param with_sibling_data: include sibling data
        :return:
        """

        if root is None:
            root = self.root

        side_nodes = []
        path_nodes = [root]

        if root == PLACEHOLDER:
            return side_nodes, path_nodes, None, None

        current_data = self.store.nodes[root]
        if current_data is None:
            return None, None, None, None
        elif is_leaf(current_data):
            return side_nodes, path_nodes, current_data, None

        side_node = None
        sibling_data = None
        for index in range(DEPTH):
            l, r = parse_node(current_data)
            if get_bit(index, path) == RIGHT:
                side_node = l
                node_hash = r
            else:
                node_hash = l
                side_node = r

            side_nodes.append(side_node)
            path_nodes.append(node_hash)

            if node_hash == PLACEHOLDER:
                current_data = None
                break

            current_data = self.store.nodes[node_hash]
            if current_data is None:
                return None, None, None, None
            elif is_leaf(current_data):
                break

        if with_sibling_data:
            sibling_data = self.store.nodes[side_node]
            if not sibling_data:
                return None, None, None, None

        return side_nodes[::-1], path_nodes[::-1], current_data, sibling_data

    def _update_with_side_nodes(
        self,
        path: bytes,
        value: bytes,
        side_nodes: Sequence[bytes],
        path_nodes: Sequence[bytes],
        old_leaf_data: bytes,
    ) -> bytes:
        value_hash = digest(value)
        current_hash, current_data = create_leaf(path, value_hash)

        self.store.nodes[current_hash] = current_data
        current_data = current_hash

        old_value_hash = None
        if path_nodes[0] == PLACEHOLDER:
            common_prefix_count = DEPTH
        else:
            actual_path, old_value_hash = parse_leaf(old_leaf_data)
            common_prefix_count = count_common_prefix(path, actual_path)

        if common_prefix_count != DEPTH:
            if get_bit(common_prefix_count, path) == RIGHT:
                current_hash, current_data = create_node(path_nodes[0], current_data)
            else:
                current_hash, current_data = create_node(current_data, path_nodes[0])

            self.store.nodes[current_hash] = current_data
            current_data = current_hash
        elif old_value_hash is not None:
            if old_value_hash == value_hash:
                return self.root

            del self.store.nodes[path_nodes[0]]
            del self.store[path]

        for path_node in path_nodes[1:]:
            del self.store.nodes[path_node]

        offset = DEPTH - len(side_nodes)
        for layer in range(DEPTH):
            if layer - offset < 0:
                if common_prefix_count != DEPTH and common_prefix_count > DEPTH - 1 - layer:
                    side_node = PLACEHOLDER
                else:
                    continue
            else:
                side_node = side_nodes[layer - offset]

            if get_bit(DEPTH - 1 - layer, path) == RIGHT:
                current_hash, current_data = create_node(side_node, current_data)
            else:
                current_hash, current_data = create_node(current_data, side_node)

            self.store.nodes[current_hash] = current_data
            current_data = current_hash

        self.store[path] = value
        return current_hash

    def _delete_with_side_nodes(
        self,
        path: bytes,
        side_nodes: Sequence[bytes],
        path_nodes: Sequence[bytes],
        old_leaf_data: bytes,
    ):
        if path_nodes[0] == PLACEHOLDER:
            # This key is already empty as it is a placeholder; return an error
            return None, KeyAlreadyEmpty
        elif parse_leaf(old_leaf_data)[0] != path:
            # This key is already empty as a different key was found its place; return an error.
            return None, KeyAlreadyEmpty

        # Remove all orphans
        for value in path_nodes:
            try:
                del self.store.nodes[value]
            except KeyError:
                return None, None

        current_hash = None
        current_data = None
        non_placeholder_reached = False
        for index, side_node in enumerate(side_nodes):
            if side_node is None:
                continue

            if current_data is None:
                side_node_value = self.store.nodes[side_node]
                if side_node_value is None:
                    return None, InvalidKey
                if is_leaf(side_node_value):
                    current_hash = side_node
                    current_data = side_node
                    continue
                else:
                    current_data = PLACEHOLDER
                    non_placeholder_reached = True

            if not non_placeholder_reached and side_node == PLACEHOLDER:
                continue
            elif not non_placeholder_reached:
                non_placeholder_reached = True

            if get_bit(len(side_nodes) - 1 - index, path) == RIGHT:
                current_hash, current_data = create_node(side_node, current_data)
            else:
                current_hash, current_data = create_node(current_data, side_node)

            self.store.nodes[current_hash] = current_data
            current_data = current_hash

        if current_hash is None:
            current_hash = PLACEHOLDER

        return current_hash, None

    def _proof(self, key: bytes, root: bytes, is_updatable: bool = False) -> SparseMerkleProof:
        if root is None:
            root = self.root

        path = digest(key)
        (
            side_nodes,
            old_leaf_hash,
            old_leaf_data,
            sibling_data,
        ) = self._side_nodes(path, root, is_updatable)

        non_empty_side_nodes = []
        for side_node in side_nodes:
            if side_node is not None:
                non_empty_side_nodes.append(side_node)

        non_membership_leaf_data = None
        if old_leaf_hash != PLACEHOLDER:
            actual_path, _ = parse_leaf(old_leaf_data)
            if path != actual_path:
                non_membership_leaf_data = old_leaf_data

        return SparseMerkleProof(non_empty_side_nodes, non_membership_leaf_data, sibling_data)
