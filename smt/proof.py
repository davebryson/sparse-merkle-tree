"""
"""
from .utils import (
    DEPTH,
    KEYSIZE,
    create_leaf,
    digest,
    LEAF,
    parse_leaf,
    get_bit,
    create_node,
    DEFAULTVALUE,
    PLACEHOLDER,
    RIGHT,
)


class SparseMerkleProof:
    def __init__(self, sidenodes, non_membership_leafdata, siblingdata):
        self.sidenodes = sidenodes
        self.non_membership_leafdata = non_membership_leafdata
        self.sibling_data = siblingdata

    def sanity_check(self):
        if (
            len(self.sidenodes) > DEPTH
            or self.non_membership_leafdata != None
            and len(self.non_membership_leafdata) != len(LEAF) + KEYSIZE + KEYSIZE
        ):
            return False

        for sn in self.sidenodes:
            if len(sn) != KEYSIZE:
                return False

        if self.sibling_data:
            sibhash = digest(self.sibling_data)
            if self.sidenodes and len(self.sidenodes) > 0:
                if self.sidenodes[0] != sibhash:
                    return False
        return True


def verify_proof(proof, root, key, value):
    path = digest(key)

    if not proof.sanity_check():
        return False

    current_hash = None
    # current_data = None

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

    for i, node in enumerate(proof.sidenodes):
        if get_bit(len(proof.sidenodes) - 1 - i, path) == RIGHT:
            current_hash, _current_data = create_node(node, current_hash)
        else:
            current_hash, _current_data = create_node(current_hash, node)

    return current_hash == root
