# PyCaching - Geocaching for Python

A Python 3 interface for working with Geocaching.com website.

Inspired by these packages (thanks to their authors):

- Geocache Grabber (by Fuad Tabba) - http://www.cs.auckland.ac.nz/~fuad/geo.py
- geocaching-py (by Lev Shamardin) - https://github.com/abbot/geocaching-py

### Features
- **login** to Geocaching.com
- **search** for up to 200 caches around any point
- **load cache** details by WP
    + normal loading (loads all details)
    + quick loading (loads just basic info very quickly)
    + **NEW:** lazy loading (create cache object and load info on demand)
- **geocode** given location

### Roadmap
- search results caching (without geo- :))
- Sphinx documentation
- submitting cache logs
- usage of asyncio
- automatic generation of possible cache attributes

## Installation

Using pip:

    pip install pycaching --pre

Manually, from GIT:

    git clone https://github.com/tomasbedrich/pycaching.git

### Requirements
- MechanicalSoup >= 0.2.0
- geopy >= 1.0.0

## Example usage

### Load a cache details

    import pycaching

    geocaching = pycaching.login("user", "pass")
    cache = geocaching.load_cache("GC12345")
    print(cache.name)

Using lazy loading:

    from pycaching import Geocaching, Cache

    gc = Geocaching.login("user", "pass")
    print(Cache("GC12345", gc).name)

### Find all traditional caches around

Notice the `limit` in search function. It is because `search()` returns a generator object, which would fetch the caches forever in case of simple loop.

    from pycaching import Geocaching, Point
    
    point = Point(10.123456, 10.123456)
    gc = Geocaching.login("user", "pass")

    for cache in gc.search(point, limit=50):
        if cache.cache_type == "Traditional Cache":
            print(cache.name)

### Find all caches on some adress

    import pycaching

    gc = pycaching.login("user", "pass")
    point = gc.geocode("10900 Euclid Ave in Cleveland")

    for cache in gc.search(point, limit=10):
        print(cache.name)

## Legal notice

Be sure to read Geocaching.com's terms of use (http://www.geocaching.com/about/termsofuse.aspx). By using this piece of software you break them and your Geocaching account may be suspended or *even deleted*. To prevent this, I recommend you to load the data you really need, nothing more. This software is provided "as is" and I am not responsible for any damage possibly caused by it.

## Author

Tomas Bedrich  
[tbedrich.cz](http://tbedrich.cz)  
ja@tbedrich.cz

____

[![Build Status](http://img.shields.io/travis/tomasbedrich/pycaching/master.svg)](https://travis-ci.org/tomasbedrich/pycaching) [![Coverage Status](https://img.shields.io/coveralls/tomasbedrich/pycaching.svg)](https://coveralls.io/r/tomasbedrich/pycaching) [![PyPI monthly downloads](http://img.shields.io/pypi/dm/PyCaching.svg)](https://pypi.python.org/pypi/PyCaching)
