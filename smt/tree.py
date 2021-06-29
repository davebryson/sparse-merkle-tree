"""
Sparse Merkle Tree.
A Python port of: https://github.com/celestiaorg/smt
"""

from .proof import SparseMerkleProof
from .store import MemoryStore, DatabaseAPI
from .utils import (
    create_node,
    create_leaf,
    count_common_prefix,
    get_bit,
    parse_leaf,
    parse_node,
    is_leaf,
    digest,
    DEPTH,
    PLACEHOLDER,
    RIGHT,
    DEFAULTVALUE,
)


# Errors
KeyAlreadyEmpty = 1
InvalidKey = 2


class SparseMerkleTree:
    def __init__(self, db: DatabaseAPI = MemoryStore(), root=PLACEHOLDER):
        self.db = db
        self.root = root

    def root_as_bytes(self):
        return self.root

    def root_as_hex(self):
        return "0x{}".format(self.root.hex())

    def get(self, key):
        """
        Get a value for the given key using the current root.
        """
        return self.get_for_root(key, self.root)

    def get_for_root(self, key, root):
        """
        Get a value for a given key using the given root.  You can lookup values
        for keys for past roots
        """

        if root == PLACEHOLDER:
            return DEFAULTVALUE

        path = digest(key)
        current_hash = root

        for i in range(0, DEPTH):
            current_data = self.db.get(current_hash)
            if current_data == None:
                return None
            if is_leaf(current_data):
                p, value_hash = parse_leaf(current_data)
                if p != path:
                    return DEFAULTVALUE

                value = self.db.get(value_hash)
                return value

            left, right = parse_node(current_data)
            if get_bit(i, path) == RIGHT:
                current_hash = right
            else:
                current_hash = left

            if current_hash == PLACEHOLDER:
                return DEFAULTVALUE

    def has(self, key):
        result = self.get(key)
        if not result:
            return False
        return result != DEFAULTVALUE

    def has_for_root(self, key, root):
        result = self.get_for_root(key, root)
        if not result:
            return False
        return result != DEFAULTVALUE

    def update(self, key, value):
        """
        Update a key value
        """
        new_root = self.update_for_root(key, value, self.root)
        self.root = new_root
        return new_root

    def update_for_root(self, key, value, root):
        path = digest(key)
        side_nodes, old_leafhash, old_leafdata, _sibdata = self._get_sidenodes(
            path, root
        )

        # If the value is the None (defaultValue) then do a delete for the key
        if value == DEFAULTVALUE:
            new_root, err = self._delete_with_sidenodes(
                path, side_nodes, old_leafdata, old_leafdata
            )
            if err and err == KeyAlreadyEmpty:
                return root
            else:
                return new_root
        else:
            return self._update_with_sidenodes(
                path, value, side_nodes, old_leafhash, old_leafdata
            )

    def delete(self, key):
        return self.update(key, DEFAULTVALUE)

    def delete_for_root(self, key, root):
        return self.update_for_root(key, DEFAULTVALUE, root)

    def prove(self, key):
        return self.prove_for_root(key, self.root)

    def prove_for_root(self, key, root):
        return self._proof_for_root(key, root, False)

    def prove_updatable(self, key):
        return self.prove_updatable(key, self.root)

    def prove_updatable_for_root(self, key, root):
        return self._proof_for_root(key, root, True)

    def _get_sidenodes(self, path, root, with_sibling_data=False):
        """
        Walk the tree down from the root, gathering neighbor nodes
        on the way to leaf for the given key (path)
        """
        side_nodes = []

        if root == PLACEHOLDER:
            return (side_nodes, PLACEHOLDER, None, None)

        current_data = self.db.get(root)
        if current_data == None:
            return (None, None, None, None)
        elif is_leaf(current_data):
            return (side_nodes, root, current_data, None)

        node_hash = None
        side_node = None
        sibdata = None
        for i in range(DEPTH):
            l, r = parse_node(current_data)
            if get_bit(i, path) == RIGHT:
                side_node = l
                node_hash = r
            else:
                side_node = r
                node_hash = l

            side_nodes.append(side_node)

            if node_hash == PLACEHOLDER:
                current_data = None
                break

            current_data = self.db.get(node_hash)
            if current_data == None:
                return (None, None, None, None)
            elif is_leaf(current_data):
                break

        if with_sibling_data:
            sibdata = self.db.get(side_node)
            if not sibdata:
                return (None, None, None, None)

        return (side_nodes[::-1], node_hash, current_data, sibdata)

    def _update_with_sidenodes(
        self, path, value, side_nodes, old_leafhash, old_leafdata
    ):
        value_hash = digest(value)
        self.db.put(value_hash, value)  # = value

        current_hash, current_data = create_leaf(path, value_hash)
        self.db.put(current_hash, current_data)  # = current_data
        current_data = current_hash

        common_prefix_count = 0
        if old_leafhash == PLACEHOLDER:
            common_prefix_count = DEPTH
        else:
            actual_path, _ = parse_leaf(old_leafdata)
            common_prefix_count = count_common_prefix(path, actual_path)

        if common_prefix_count != DEPTH:
            if get_bit(common_prefix_count, path) == RIGHT:
                current_hash, current_data = create_node(old_leafhash, current_data)
            else:
                current_hash, current_data = create_node(current_data, old_leafhash)

            self.db.put(current_hash, current_data)  # = current_data
            current_data = current_hash  # HEREE!!!

        offset = DEPTH - len(side_nodes)
        for i in range(DEPTH):
            side_node = bytes(32)
            if (i - offset) < 0:
                if common_prefix_count != DEPTH and common_prefix_count > DEPTH - 1 - i:
                    side_node = PLACEHOLDER
                else:
                    continue
            else:
                side_node = side_nodes[i - offset]

            if get_bit(DEPTH - 1 - i, path) == RIGHT:
                current_hash, current_data = create_node(side_node, current_data)
            else:
                current_hash, current_data = create_node(current_data, side_node)

            self.db.put(current_hash, current_data)  # = current_data
            current_data = current_hash

        return current_hash

    # return (root, error)
    def _delete_with_sidenodes(self, path, sidenodes, old_leafhash, old_leafdata):
        if old_leafhash == PLACEHOLDER:
            # This key is already empty as it is a placeholder; return an error
            return (None, KeyAlreadyEmpty)

        if parse_leaf(old_leafdata)[0] != path:
            # This key is already empty as a different key was found its place; return an error.
            return (None, KeyAlreadyEmpty)

        current_hash = None
        current_data = None
        non_placeholder_reached = False
        for i, sn in enumerate(sidenodes):
            if sn == None:
                continue

            if current_data == None:
                side_node_value = self.db.get(sn)
                if side_node_value == None:
                    return (None, InvalidKey)
                if is_leaf(side_node_value):
                    current_hash = sn
                    current_data = sn
                    continue
                else:
                    current_data = PLACEHOLDER
                    non_placeholder_reached = True

            if not non_placeholder_reached and sn == PLACEHOLDER:
                continue
            elif not non_placeholder_reached:
                non_placeholder_reached = True

            if get_bit(len(sidenodes) - 1 - i, path) == RIGHT:
                current_hash, current_data = create_node(sn, current_data)
            else:
                current_hash, current_data = create_node(current_data, sn)

            self.db.put(current_hash, current_data)  # = current_data
            current_data = current_hash

        if current_hash == None:
            current_hash = PLACEHOLDER

        return (current_hash, None)

    def _proof_for_root(self, key, root, is_updatable):
        path = digest(key)
        side_nodes, old_leafhash, old_leafdata, sibdata = self._get_sidenodes(
            path, root, is_updatable
        )

        non_empty_sides = []
        for sn in side_nodes:
            if sn != None:
                non_empty_sides.append(sn)

        non_membership_leafdata = None
        if old_leafhash != PLACEHOLDER:
            actual_path, _ = parse_leaf(old_leafdata)
            if path != actual_path:
                non_membership_leafdata = old_leafdata

        return SparseMerkleProof(non_empty_sides, non_membership_leafdata, sibdata)
