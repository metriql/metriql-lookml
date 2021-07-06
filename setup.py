#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise ValueError("Requires Python 3.6+")

from metriql2lookml import __version__

with open("requirements.txt", "r") as f:
    requires = [x.strip() for x in f if x.strip()]

with open("requirements-test.txt", "r") as f:
    test_requires = [x.strip() for x in f if x.strip()]

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="metriql-lookml",
    version=__version__,
    description="metriql Looker integration",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Umar Majeed",
    author_email="emre@rakam.io",
    url="https://github.com/metriql/lookml-generator",
    license="MIT License",
    packages=find_packages(exclude=["tests"]),
    test_suite="tests",
    scripts=["metriql2lookml/bin/metriql-lookml"],
    tests_require=test_requires,
    install_requires=requires,
    extras_require={"test": test_requires},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)