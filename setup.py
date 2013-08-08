#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup
import os


here = os.path.dirname(os.path.abspath(__file__))

try:
    f = open(os.path.join(here, 'README.txt'))
    long_description = f.read()
except:
    long_description = "A Python interface for working with Geocaching.com website."

setup(    
    name='PyCaching',
    version="0.1.2",
    author='Tomas Bedrich',
    author_email='ja@tbedrich.cz',
    url = 'https://github.com/tomasbedrich/pycaching',
    packages=['pycaching'],
    license='GNU Lesser General Public License (LGPL)',
    description='Geocaching.com site crawler. Searches and loads caches.',
    long_description=long_description,
    keywords = ['geocaching', 'robot', 'crawler', 'geocache', 'cache'],
    install_requires=[
        "BeautifulSoup >= 3.2.1",
        "geopy == 0.95.1",
    ],
)