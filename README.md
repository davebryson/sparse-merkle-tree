# Sparse Merkle Tree

A Sparse Merkle Tree for a key/value map.

This is a Python port of the great work here: [celestiaorg](https://github.com/celestiaorg/smt)

> The tree implements the same optimisations specified in the Libra whitepaper, to reduce the number of hash operations required per tree operation to O(k) where k is the number of non-empty elements in the tree.


## Example

```python
tree = SparseMerkleTree()
root = tree.update(b"a", b"a1")

assert b"a1" == tree.get(b"a")

proof = tree.prove(b"a")
assert verify_proof(proof, root, b"a", b"a1")
```
