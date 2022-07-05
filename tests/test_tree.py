from typing import Dict

import pytest

from sparsemerkletree import SparseMerkleTree
from sparsemerkletree.proof import verify_proof
from sparsemerkletree.utils import DEFAULTVALUE, PLACEHOLDER


def test_tree_basics():
    tree = SparseMerkleTree()

    assert tree[b"c"] == DEFAULTVALUE

    tree[b"a"] = b"a1"
    root_0 = tree.root

    assert len(root_0) == 32
    assert root_0 != PLACEHOLDER

    tree[b"b"] = b"b1"
    tree[b"c"] = b"c1"
    tree[b"d"] = b"d1"
    tree[b"e"] = b"e1"

    tree[b"f"] = b"f1"
    root_1 = tree.root

    assert len(root_1) == 32
    assert root_1 != root_0

    assert tree[b"a"] == b"a1"
    assert tree[b"b"] == b"b1"
    assert tree[b"c"] == b"c1"
    assert tree[b"d"] == b"d1"
    assert tree[b"e"] == b"e1"
    assert tree[b"f"] == b"f1"
    assert tree[b"nope"] == b""

    del tree[b"c"]
    root_2 = tree.root

    assert len(root_2) == 32

    assert tree[b"c"] == DEFAULTVALUE
    assert tree[b"a"] == b"a1"
    assert tree[b"b"] == b"b1"
    assert tree[b"d"] == b"d1"
    assert tree[b"e"] == b"e1"
    assert tree[b"f"] == b"f1"

    # has it...
    assert b"e" in tree

    # update existing key
    tree[b"b"] = b"b11"
    root_3 = tree.root

    assert len(root_3) == 32
    assert root_3 != root_2
    assert tree[b"b"] == b"b11"

    # test updating a key still allows getting values from old roots
    tree[b"b"] = b"b111"
    root_4 = tree.root

    assert tree[b"b"] == b"b111"
    assert root_4 != root_3

    # test you can delete a key
    del tree[b"a"]

    assert len(tree.root) > 0
    assert tree[b"a"] == DEFAULTVALUE


def test_proofs():
    tree = SparseMerkleTree()

    tree[b"b"] = b"b1"

    assert tree.root

    tree[b"c"] = b"c1"

    assert tree.root

    tree[b"d"] = b"d1"

    assert tree.root

    tree[b"e"] = b"e1"

    assert tree.root

    del tree[b"c"]

    assert tree.root

    tree[b"f"] = b"f1"
    root = tree.root

    proof_1 = tree.prove(b"d")
    proof_2 = tree.prove(b"np")
    proof_3 = tree.prove(b"c")

    assert verify_proof(proof_1, root, key=b"d", value=b"d1")
    assert not verify_proof(proof_2, root, key=b"np", value=b"np1")
    assert verify_proof(proof_3, root, key=b"c", value=DEFAULTVALUE)


def test_bulk(data):
    tree = SparseMerkleTree.from_data(data)

    assert tree == data

    root = tree.root
    for key, value in data.items():
        proof = tree.prove(key)

        assert proof.sanity_check()
        assert verify_proof(proof, root, key=key, value=value)

    for key in data:
        del tree[key]
        assert tree.root is not None

    assert all(tree[key] == b"" for key in data)


@pytest.fixture
def data(size: int = 500) -> Dict[bytes, bytes]:
    import secrets
    import random

    return {
        secrets.token_bytes(random.randint(10, 30)): secrets.token_bytes(
            random.randint(30, 500)
        )
        for _ in range(size)
    }
