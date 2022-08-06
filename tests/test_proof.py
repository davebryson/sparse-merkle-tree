from sparsemerkletree import SparseMerkleTree
from sparsemerkletree.proof import verify_proof
from sparsemerkletree.utils import DEFAULTVALUE

# noinspection PyUnresolvedReferences
from tests import random_data, sample_tree


def test_proof():
    tree = SparseMerkleTree()

    tree[b"b"] = b"b1"
    tree[b"c"] = b"c1"
    tree[b"d"] = b"d1"
    tree[b"e"] = b"e1"
    del tree[b"c"]
    tree[b"f"] = b"f1"

    root = tree.root

    proof_1 = tree.prove(b"d")
    proof_2 = tree.prove(b"np")
    proof_3 = tree.prove(b"c")

    assert verify_proof(proof_1, root, key=b"d", value=b"d1")
    assert not verify_proof(proof_2, root, key=b"np", value=b"np1")
    assert verify_proof(proof_3, root, key=b"c", value=DEFAULTVALUE)


def test_random_data(random_data):
    tree = SparseMerkleTree.from_data(random_data)

    root = tree.root
    for key, value in random_data.items():
        proof = tree.prove(key)

        assert proof.sanity_check()
        assert verify_proof(proof, root, key=key, value=value)
