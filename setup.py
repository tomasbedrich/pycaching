#!/usr/bin/env python3

import os
from setuptools import setup

root = os.path.dirname(__file__) or "."
f = open(os.path.join(root, "README.rst"))
long_description = f.read()

info = {
    "name":                "pycaching",
    "version":             "3.1.1",  # PEP 386
    "author":              "Tomas Bedrich",
    "author_email":        "ja@tbedrich.cz",
    "url":                 "https://github.com/tomasbedrich/pycaching",
    "packages":            ["pycaching"],
    "provides":            ["pycaching"],
    "license":             "GNU Lesser General Public License (LGPL) v3.0",
    "description":         "Geocaching.com site crawler. Provides tools for searching, fetching caches and geocoding.",
    "long_description":    long_description,
    "keywords":            ["geocaching", "crawler", "geocache", "cache", "searching", "geocoding"],
    "install_requires":    ["MechanicalSoup >= 0.3.0", "geopy >= 1.0.0"],
    "test_suite":          "test"
}

setup(**info)
