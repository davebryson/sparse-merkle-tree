from typing import Dict

import pytest

from sparsemerkletree import SparseMerkleTree


@pytest.fixture(scope="session", autouse=True)
def random_data(size: int = 500) -> Dict[bytes, bytes]:
    import secrets
    import random

    return {secrets.token_bytes(random.randint(10, 30)): secrets.token_bytes(random.randint(30, 500)) for _ in range(size)}


@pytest.fixture(scope="session", autouse=True)
def sample_tree() -> SparseMerkleTree:
    tree = SparseMerkleTree()

    tree[b"b"] = b"b1"
    tree[b"c"] = b"c1"
    tree[b"d"] = b"d1"
    tree[b"e"] = b"e1"
    tree[b"f"] = b"f1"

    return tree
