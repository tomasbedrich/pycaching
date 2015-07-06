=================================
pycaching - Geocaching for Python
=================================

A Python 3 interface for working with Geocaching.com website.

--------
Features
--------

-  **login** to Geocaching.com
-  **search** caches
   
   - normal search (unlimited number of caches from any point)
   - quick search (all caches inside some area)
   
-  **load cache** details by WP

   -  normal loading (loads all details)
   -  quick loading (loads just basic info very quickly)
   -  lazy loading (create cache object and load info on demand)

-  **load trackable** details by tracking-code
-  **geocode** given location

Roadmap
~~~~~~~

-  search results caching (not geo- :)
-  Sphinx documentation
-  submitting cache logs
-  usage of asyncio
-  automatic generation of possible cache attributes - partially done


------------
Installation
------------

Using pip:

.. code:: bash

    pip install pycaching

Manually, from GIT:

.. code:: bash

    git clone https://github.com/tomasbedrich/pycaching.git

Requirements
~~~~~~~~~~~~

-  Python >= 3.0 (>= 3.4 required for running tests)
-  MechanicalSoup >= 0.3.0
-  geopy >= 1.0.0


-------------
Example usage
-------------

Login
~~~~~

.. code:: python

    import pycaching
    geocaching = pycaching.login("user", "pass")

The above is just shortcut for:

.. code:: python

    from pycaching import Geocaching
    geocaching = Geocaching()
    geocaching.login("user", "pass")

Load a cache details
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import pycaching

    geocaching = pycaching.login("user", "pass")
    cache = geocaching.load_cache("GC12345")
    print(cache.name)

Using lazy loading:

.. code:: python

    from pycaching import Geocaching, Cache

    geocaching = Geocaching()
    geocaching.login("user", "pass")
    cache = Cache("GC12345", geocaching)
    print(cache.name)

The difference is, that ``Cache`` object is created immediately and the
page is loaded when needed (accessing the name).

Find all traditional caches around
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the ``limit`` in search function. It is because ``search()``
returns a generator object, which would fetch the caches forever in case
of simple loop.

.. code:: python

    from pycaching import Geocaching, Point

    point = Point(10.123456, 10.123456)
    geocaching = Geocaching()
    geocaching.login("user", "pass")

    for cache in geocaching.search(point, limit=50):
        if cache.cache_type == "Traditional Cache":
            print(cache.name)

Find all caches on some adress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import pycaching

    geocaching = pycaching.login("user", "pass")
    point = geocaching.geocode("10900 Euclid Ave in Cleveland")

    for cache in geocaching.search(point, limit=10):
        print(cache.name)

Find approximate location of caches in area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from pycaching import Geocaching, Point, Rectangle

    geocaching = pycaching.Geocaching()
    geocaching.login("user", "pass")
    rect = Rectangle(Point(60.15, 24.95), Point(60.17, 25.00))

    for c in geocaching.search_quick(rect, strict=True):
        print('{:8} ({:.5f}, {:.5f}) (+- {:.1f} m); {}'.format(
            c.wp, c.location.latitude, c.location.longitude,
            c.location.precision, c.name))


Load trackable details
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import pycaching
    geocaching = pycaching.login("user", "pass")
    travelbug = geocaching.load_trackable("TB3ZGT2")
    print("Goal:\n", travelbug.goal,
        "\n\nDescription:\n", travelbug.description,
        "\n\nCurrent Location:\n", travelbug.location)


Find all nearby caches with trackables in them
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the ``limit`` in search function. It is because ``search()``
returns a generator object, which would fetch the caches forever in case
of simple loop.

.. code:: python

    from pycaching import Geocaching, Point

    point = Point(56.25263, 15.26738)
    geocaching = Geocaching()
    geocaching.login("user", "pass")

    for cache in geocaching.search(point, limit=50):
        if len(cache.trackables) > 0:
            print(cache.name)


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

| Tomas Bedrich
| `tbedrich.cz <http://tbedrich.cz>`__
| ja@tbedrich.cz

------------------------------------------------------------------------------------

|Build Status| |Coverage Status| |PyPI monthly downloads|

.. |Build Status| image:: http://img.shields.io/travis/tomasbedrich/pycaching/master.svg
   :target: https://travis-ci.org/tomasbedrich/pycaching

.. |Coverage Status| image:: https://img.shields.io/coveralls/tomasbedrich/pycaching.svg
   :target: https://coveralls.io/r/tomasbedrich/pycaching

.. |PyPI monthly downloads| image:: http://img.shields.io/pypi/dm/pycaching.svg
   :target: https://pypi.python.org/pypi/pycaching
