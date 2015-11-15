=================================
pycaching - Geocaching for Python
=================================

--------
Features
--------

-  **login** to Geocaching.com
-  **search** caches

   - normal search (unlimited number of caches from any point)
   - quick search (all caches inside some area)

-  **load cache** and its details

   -  normal loading (loads all details)
   -  quick loading (loads just basic info very quickly)
   -  lazy loading (create cache object and load info on demand)
   -  load logbook for given cache

-  **post log** to cache logbook
-  **load trackable** details by tracking code
-  **geocode** given location


------------
Installation
------------

Stable version - using pip:

.. code:: bash

    pip install pycaching

Dev version - manually from GIT:

.. code:: bash

    git clone https://github.com/tomasbedrich/pycaching.git
    pip install ./pycaching

Pycaching has following requirements:

.. code::

  Python>=3.4
  requests >= 2.8
  beautifulsoup4 >= 4.4
  geopy>=1.11


-------------
Example usage
-------------

Login
~~~~~

.. code:: python

    import pycaching
    geocaching = pycaching.login("user", "pass")

Load a cache details
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    cache = geocaching.get_cache("GC1PAR2")
    print(cache.name)  # cache.load() is automatically called
    print(cache.location)  # stored in cache, printed immediately

This uses lazy loading, so the ``Cache`` object is created immediately and the
page is loaded when needed (accessing the name).

You can use different method of loading cache details. It will be much faster,
but it will load less details:

.. code:: python

    cache = geocaching.get_cache("GC1PAR2")
    cache.load_quick()  # takes a small while
    print(cache.name)  # stored in cache, printed immediately
    print(cache.location)  # NOT stored in cache, will trigger full loading

You can also load a logbook for cache:

.. code:: python

    for log in cache.load_logbook(limit=200):
        print(log.visited, log.type, log.author, log.text)

Or its trackables:

.. code:: python

    for trackable in cache.load_trackables(limit=5):
        print(trackable.name)

Post a log to cache
~~~~~~~~~~~~~~~~~~~

.. code:: python

    geocaching.post_log("GC1PAR2", "Found cache in the rain. Nice Place, TFTC!")

It is also possible to call post_log on ``Cache`` object, but you would have
to create ``Log`` object manually and pass it to this method.

Search for all traditional caches around
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pycaching import Point
    from pycaching.cache import Type

    point = Point(56.25263, 15.26738)

    for cache in geocaching.search(point, limit=50):
        if cache.type == Type.traditional:
            print(cache.name)

Notice the ``limit`` in search function. It is because ``search()``
returns a generator object, which would fetch the caches forever in case
of simple loop.

Geocode adress and search around
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    point = geocaching.geocode("Prague")

    for cache in geocaching.search(point, limit=10):
        print(cache.name)

Find caches with their approximate locations in some area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pycaching import Point, Rectangle

    rect = Rectangle(Point(60.15, 24.95), Point(60.17, 25.00))

    for cache in geocaching.search_quick(rect, strict=True):
        print(cache.name, cache.location.precision)


Load a trackable details
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    trackable = geocaching.get_trackable("TB3ZGT2")
    print(trackable.name, trackable.goal, trackable.description, trackable.location)


--------
Appendix
--------

Legal notice
~~~~~~~~~~~~

Be sure to read `Geocaching.com's terms of
use <http://www.geocaching.com/about/termsofuse.aspx>`__. By using this
piece of software you break them and your Geocaching account may be
suspended or *even deleted*. To prevent this, I recommend you to load
the data you really need, nothing more. This software is provided "as
is" and I am not responsible for any damage possibly caused by it.

Inspiration
~~~~~~~~~~~

Original version was inspired by these packages:

-  `Geocache Grabber <http://www.cs.auckland.ac.nz/~fuad/geo.py>`__ (by Fuad Tabba)
-  `geocaching-py <https://github.com/abbot/geocaching-py>`__ (by Lev Shamardin)

Although the new version was massively rewritten, I'd like to thank to their authors.

Author
~~~~~~

| Tomáš Bedřich
| `tbedrich.cz <http://tbedrich.cz>`__
| ja@tbedrich.cz

Thanks to `all contributors <https://github.com/tomasbedrich/pycaching/graphs/contributors>`__!

------------------------------------------------------------------------------------

|Build Status| |Coverage Status| |PyPI monthly downloads|

.. |Build Status| image:: http://img.shields.io/travis/tomasbedrich/pycaching/master.svg
   :target: https://travis-ci.org/tomasbedrich/pycaching

.. |Coverage Status| image:: https://img.shields.io/coveralls/tomasbedrich/pycaching.svg
   :target: https://coveralls.io/r/tomasbedrich/pycaching

.. |PyPI monthly downloads| image:: http://img.shields.io/pypi/dm/pycaching.svg
   :target: https://pypi.python.org/pypi/pycaching
