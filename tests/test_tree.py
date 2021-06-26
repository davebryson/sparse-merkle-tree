from smt.tree import SparseMerkleTree
from smt.utils import DEFAULTVALUE
from smt.proof import verify_proof


def test_tree_basics():
    tree = SparseMerkleTree()

    assert DEFAULTVALUE == tree.get(b"c")

    root1 = tree.update(b"a", b"a1")
    assert 32 == len(root1)

    assert tree.update(b"b", b"b1")
    assert tree.update(b"c", b"c1")
    assert tree.update(b"d", b"d1")
    assert tree.update(b"e", b"e1")
    rootn = tree.update(b"f", b"f1")

    assert 32 == len(rootn)
    assert root1 != rootn

    assert b"a1" == tree.get(b"a")
    assert b"b1" == tree.get(b"b")
    assert b"c1" == tree.get(b"c")
    assert b"d1" == tree.get(b"d")
    assert b"e1" == tree.get(b"e")
    assert b"f1" == tree.get(b"f")

    rootn1 = tree.delete(b"c")
    assert 32 == len(rootn1)

    assert DEFAULTVALUE == tree.get(b"c")
    assert b"a1" == tree.get(b"a")
    assert b"b1" == tree.get(b"b")
    assert b"d1" == tree.get(b"d")
    assert b"e1" == tree.get(b"e")
    assert b"f1" == tree.get(b"f")

    # has it...
    assert tree.has(b"e")
    assert tree.has_for_root(b"d", rootn1)
    assert tree.has_for_root(b"c", rootn)

    # update existing key
    rootn2 = tree.update(b"b", b"b11")
    assert 32 == len(rootn2)
    assert rootn2 != rootn1
    assert b"b11" == tree.get(b"b")

    # test updating a key still allows getting values from old roots
    rootn3 = tree.update(b"b", b"b111")
    assert b"b11" == tree.get_for_root(b"b", rootn2)
    assert b"b111" == tree.get(b"b")
    assert rootn3 != rootn2

    # test you can update a key in an older root
    rootn4 = tree.update_for_root(b"b", b"b1111", rootn2)
    assert b"b1111" == tree.get_for_root(b"b", rootn4)
    assert b"b111" == tree.get(b"b")
    assert DEFAULTVALUE == tree.get(b"c")

    # test you can delete a key in an old root
    # delete 'a' in rootn2
    rootn5 = tree.delete_for_root(b"a", rootn2)
    assert DEFAULTVALUE == tree.get_for_root(b"a", rootn5)
    assert b"a1" == tree.get(b"a")


def test_proofs():
    tree = SparseMerkleTree()
    assert tree.update(b"b", b"b1")
    assert tree.update(b"c", b"c1")
    assert tree.update(b"d", b"d1")
    assert tree.update(b"e", b"e1")

    assert tree.delete(b"c")

    root = tree.update(b"f", b"f1")

    proof = tree.prove(b"d")
    assert verify_proof(proof, root, b"d", b"d1")

    proof1 = tree.prove(b"nope")
    assert not verify_proof(proof1, root, b"np", b"np1")

    proof2 = tree.prove(b"c")
    assert verify_proof(proof2, root, b"c", DEFAULTVALUE)


def test_bulk():
    data = make_random_data()
    tree = SparseMerkleTree()
    for k, v in data:
        assert tree.update(k, v)

    for k, v in data:
        assert v == tree.get(k)

    root = tree.root
    for k, v in data:
        proof = tree.prove(k)
        assert proof.sanity_check()
        assert verify_proof(proof, root, k, v)


def make_random_data(size=500):
    import secrets
    import random

    return [
        (
            secrets.token_bytes(random.randint(10, 30)),
            secrets.token_bytes(random.randint(30, 500)),
        )
        for _ in range(size)
    ]
