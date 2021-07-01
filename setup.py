#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

DIR = path.abspath(path.dirname(__file__))

with open(path.join(DIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sparse-merkle-tree",
    version="0.2.0",
    description="A Sparse Merkle Tree for a key/value map",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davebryson/sparse-merkle-tree",
    author="Dave Bryson",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="merkle tree",
    packages=["smt"],
    install_requires=[],
    test_require=["pytest>=6.2.4"],
    python_requires=">=3.9",
)
