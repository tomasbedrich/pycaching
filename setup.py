#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup
import os

here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here, 'README.md'))
long_description = f.read()

setup(    
    name='PyCaching',
    version="0.1.dev",
    author='Tomas Bedrich',
    author_email='ja@tbedrich.cz',
    packages=['pycaching'],
    license='GNU Lesser General Public License (LGPL)',
    description='Geocaching.com site crawler. Searches and loads caches.',
    long_description=long_description,
    install_requires=[
        "BeautifulSoup >= 3.2.1",
        "geopy == 0.95.1",
    ],
)