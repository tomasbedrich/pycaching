#!/usr/bin/env python3

from setuptools import setup
import os

from pycaching import __version__


root = os.path.dirname(__file__) or "."

try:
    f = open(os.path.join(root, "README.txt"))
    long_description = f.read()
except FileNotFoundError:
    long_description = "A Python interface for working with Geocaching.com website."

setup(
    name="PyCaching",
    version=__version__,
    author="Tomas Bedrich",
    author_email="ja@tbedrich.cz",
    url="https://github.com/tomasbedrich/pycaching",
    packages=["pycaching"],
    license="GNU Lesser General Public License (LGPL)",
    description="Geocaching.com site crawler. Searches and loads caches.",
    long_description=long_description,
    keywords=["geocaching", "robot", "crawler", "geocache", "cache"],
    install_requires=[
        "MechanicalSoup >= 0.2.0",
        "geopy >= 1.0.0",
    ],
)
