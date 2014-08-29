#!/usr/bin/env python3

import os
from setuptools import setup

from pycaching import __version__


root = os.path.dirname(__file__) or "."
f = open(os.path.join(root, "README.rst"))
long_description = f.read()

info = {
    "name":                "PyCaching",
    "version":             __version__,
    "author":              "Tomas Bedrich",
    "author_email":        "ja@tbedrich.cz",
    "url":                 "https://github.com/tomasbedrich/pycaching",
    "packages":            ["pycaching"],
    "provides":            ["pycaching"],
    "license":             "GNU Lesser General Public License (LGPL)",
    "description":         "Geocaching.com site crawler. Searches and loads caches.",
    "long_description":    long_description,
    "keywords":            ["geocaching", "robot", "crawler", "geocache", "cache"],
    "install_requires":    ["MechanicalSoup >= 0.2.0", "geopy >= 1.0.0"],
    "test_suite":          "test"
}

setup(**info)
