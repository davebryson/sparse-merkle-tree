from sparsemerkletree import SparseMerkleTree
from sparsemerkletree.utils import DEFAULTVALUE, PLACEHOLDER

# noinspection PyUnresolvedReferences
from tests import random_data, sample_tree


def test_empty(sample_tree):
    empty_tree = SparseMerkleTree()

    assert empty_tree[b"c"] == DEFAULTVALUE
    assert sample_tree[b"c"] != DEFAULTVALUE


def test_insert_contains_update_delete():
    tree = SparseMerkleTree()

    tree[b"a"] = b"a1"
    root_1 = tree.root

    assert len(root_1) == 32
    assert root_1 != PLACEHOLDER

    tree[b"b"] = b"b1"
    tree[b"c"] = b"c1"
    tree[b"d"] = b"d1"
    tree[b"e"] = b"e1"
    tree[b"f"] = b"f1"

    root_2 = tree.root

    assert len(root_2) == 32
    assert root_2 != root_1

    assert tree[b"a"] == b"a1"
    assert tree[b"b"] == b"b1"
    assert tree[b"c"] == b"c1"
    assert tree[b"d"] == b"d1"
    assert tree[b"e"] == b"e1"
    assert tree[b"f"] == b"f1"
    assert tree[b"nope"] == b""

    del tree[b"c"]
    root_3 = tree.root

    assert len(root_3) == 32

    assert tree[b"c"] == DEFAULTVALUE
    assert tree[b"a"] == b"a1"
    assert tree[b"b"] == b"b1"
    assert tree[b"d"] == b"d1"
    assert tree[b"e"] == b"e1"
    assert tree[b"f"] == b"f1"

    # contains
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


def test_from_data(random_data):
    tree = SparseMerkleTree.from_data(random_data)

    assert tree == random_data

    for key in random_data:
        del tree[key]
        assert tree.root is not None

    assert all(tree[key] == b"" for key in random_data)
