# Sparse Merkle Tree

[![test](https://github.com/zacharyburnett/sparsemerkletree/actions/workflows/test.yml/badge.svg)](https://github.com/zacharyburnett/sparsemerkletree/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/zacharyburnett/sparsemerkletree/branch/main/graph/badge.svg?token=WQ1QLITIHI)](https://codecov.io/gh/zacharyburnett/sparsemerkletree)
[![build](https://github.com/zacharyburnett/sparsemerkletree/actions/workflows/build.yml/badge.svg)](https://github.com/zacharyburnett/sparsemerkletree/actions/workflows/build.yml)
[![version](https://img.shields.io/pypi/v/sparsemerkletree)](https://pypi.org/project/sparsemerkletree)
[![style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`sparsemerkletree` provides an interface for building a Sparse Merkle Tree for a
key / value map. This package is forked
from [Dave Bryson's Python implementation](https://github.com/davebryson/sparse-merkle-tree)
, which in turn is ported from [celestiaorg](https://github.com/celestiaorg/smt)
.

> The tree implements the same optimisations specified in the Libra
> whitepaper, to reduce the number of hash operations required per tree
> operation to O(k) where k is the number of non-empty elements in the tree.

## Installation

0. Install Python with `pip`
1. Use `pip` to install `sparsemerkletree` from PyPI:
    ```shell
    pip install sparsemerkletree
    ```

## Usage

```python
from sparsemerkletree import SparseMerkleTree
from sparsemerkletree.proof import verify_proof

tree = SparseMerkleTree()

tree[b"a"] = b"a1"

assert tree[b"a"] == b"a1"

proof = tree.prove(b"a")

assert verify_proof(proof, tree.root, key=b"a", value=b"a1")

del tree[b"a"]

assert tree[b"a"] == b""
```

