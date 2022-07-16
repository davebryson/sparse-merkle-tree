"""
module implementation of Merkle proofs
"""
from typing import Sequence

from .utils import (
    DEFAULTVALUE,
    DEPTH,
    KEYSIZE,
    LEAF,
    PLACEHOLDER,
    RIGHT,
    create_leaf,
    create_node,
    digest,
    get_bit,
    parse_leaf,
)


class SparseMerkleProof:
    def __init__(
        self,
        side_nodes: Sequence[bytes],
        non_membership_leafdata: bytes,
        sibling_data: bytes,
    ):
        self.side_nodes = side_nodes
        self.non_membership_leafdata = non_membership_leafdata
        self.sibling_data = sibling_data

    def sanity_check(self):
        if (
            len(self.side_nodes) > DEPTH
            or self.non_membership_leafdata is not None
            and len(self.non_membership_leafdata) != len(LEAF) + KEYSIZE + KEYSIZE
        ):
            return False

        for sn in self.side_nodes:
            if len(sn) != KEYSIZE:
                return False

        if self.sibling_data:
            sibhash = digest(self.sibling_data)
            if self.side_nodes and len(self.side_nodes) > 0:
                if self.side_nodes[0] != sibhash:
                    return False
        return True


def verify_proof(proof: SparseMerkleProof, root: bytes, key: bytes, value: bytes) -> bool:
    path = digest(key)

    if not proof.sanity_check():
        return False

    if value == DEFAULTVALUE:
        if not proof.non_membership_leafdata:
            current_hash = PLACEHOLDER
        else:
            actual_path, value_hash = parse_leaf(proof.non_membership_leafdata)
            if actual_path == path:
                return False
            current_hash, _current_data = create_leaf(actual_path, value_hash)
    else:
        value_hash = digest(value)
        current_hash, _current_data = create_leaf(path, value_hash)

    for i, node in enumerate(proof.side_nodes):
        if get_bit(len(proof.side_nodes) - 1 - i, path) == RIGHT:
            current_hash, _current_data = create_node(node, current_hash)
        else:
            current_hash, _current_data = create_node(current_hash, node)

    return current_hash == root
