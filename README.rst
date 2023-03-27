===================================================================================================
pycaching - Geocaching for Python
===================================================================================================

Complete documentation can be found at `Read the Docs <http://pycaching.readthedocs.org/>`_.

.. _features:

Features
===================================================================================================

-  **login** to Geocaching.com
-  **search** caches

   - normal search (unlimited number of caches from any point)
   - quick search (all caches inside some area) - currently not working, see below

-  **get cache** and its details

   -  normal loading (can load all details)
   -  quick loading (can load just basic info but very quickly)
   -  load logbook for given cache

-  **get trackable** details by tracking code
-  **post log** for a cache or a trackable
-  **geocode** given location

.. _installation:

Installation
===================================================================================================

Stable version - using pip:

.. code-block:: bash

    pip install pycaching

Dev version - manually from GIT:

.. code-block:: bash

    git clone https://github.com/tomasbedrich/pycaching.git
    cd pycaching
    pip install .

Pycaching has following requirements:

.. code::

    Python>=3.5
    requests>=2.8
    beautifulsoup4>=4.9
    geopy>=1.11

Pycaching tests have the following additional requirements:

.. code::

    betamax >=0.8, <0.9
    betamax-serializers >=0.2, <0.3

Examples
===================================================================================================

Login
---------------------------------------------------------------------------------------------------

Simply call `pycaching.login()
<https://pycaching.readthedocs.io/en/latest/api.html#pycaching.geocaching.Geocaching.login>`__
method and it will do everything for you.

.. code-block:: python

    import pycaching
    geocaching = pycaching.login("user", "pass")

If you won't provide an username or password, pycaching will try to load ``.gc_credentials`` file
from current directory or home folder. It will try to parse it as JSON and use the keys ``username``
and ``password`` from that file as login credentials.

.. code-block:: json

   { "username": "myusername", "password": "mypassword" }


You can also provide multiple username and password tuples in a file as login credentials.
The tuple to be used can be chosen by providing its username when calling ``pycaching.login()``,
e.g. ``pycaching.login("myusername2")``. The first username and password tuple specified will be
used as default if ``pycaching.login()`` is called without providing a username.

.. code-block:: json

   [ { "username": "myusername1", "password": "mypassword1" },
     { "username": "myusername2", "password": "mypassword2" } ]


.. code-block:: python

    import pycaching
    geocaching = pycaching.login()  # assume the .gc_credentials file is presented

In case you have a password manager in place featuring a command line interface
(e.g. `GNU pass <https://www.passwordstore.org/>`__) you may specify a password retrieval command
using the ``password_cmd`` key instead of ``password``.

.. code-block:: json

   { "username": "myusername", "password_cmd": "pass geocaching.com/myUsername" }

Note that the ``password`` and ``password_cmd`` keys are mutually exclusive.



Load a cache details
---------------------------------------------------------------------------------------------------

.. code-block:: python

    cache = geocaching.get_cache("GC1PAR2")
    print(cache.name)  # cache.load() is automatically called
    print(cache.location)  # stored in cache, printed immediately

This uses lazy loading, so the `Cache <https://pycaching.readthedocs.io/en/latest/api.html#cache>`__
object is created immediately and the page is loaded when needed (accessing the name).

You can use a different method of loading cache details. It will be much faster, but it will load less
details:

.. code-block:: python

    cache = geocaching.get_cache("GC1PAR2")
    cache.load_quick()  # takes a small while
    print(cache.name)  # stored in cache, printed immediately
    print(cache.location)  # NOT stored in cache, will trigger full loading

You can also load a logbook for cache:

.. code-block:: python

    for log in cache.load_logbook(limit=200):
        print(log.visited, log.type, log.author, log.text)

Or its trackables:

.. code-block:: python

    for trackable in cache.load_trackables(limit=5):
        print(trackable.name)

Post a log to cache
---------------------------------------------------------------------------------------------------

.. code-block:: python

    geocaching.post_log("GC1PAR2", "Found cache in the rain. Nice place, TFTC!")

It is also possible to call ``post_log`` on `Cache
<https://pycaching.readthedocs.io/en/latest/api.html#cache>`__ object, but you would have to create
`Log <https://pycaching.readthedocs.io/en/latest/api.html#log>`__ object manually and pass it to
this method.

Search for all traditional caches around
---------------------------------------------------------------------------------------------------

.. code-block:: python

    from pycaching import Point
    from pycaching.cache import Type

    point = Point(56.25263, 15.26738)

    for cache in geocaching.search(point, limit=50):
        if cache.type == Type.traditional:
            print(cache.name)

Notice the ``limit`` in the search function. It is because `geocaching.search()
<https://pycaching.readthedocs.io/en/latest/api.html#pycaching.geocaching.Geocaching.search>`__
returns a generator object, which would fetch the caches forever in case of a simple loop.

Geocode address and search around
---------------------------------------------------------------------------------------------------

.. code-block:: python

    point = geocaching.geocode("Prague")

    for cache in geocaching.search(point, limit=10):
        print(cache.name)

Find caches in some area
---------------------------------------------------------------------------------------------------

.. code-block:: python

    from pycaching import Point, Rectangle

    rect = Rectangle(Point(60.15, 24.95), Point(60.17, 25.00))

    for cache in geocaching.search_rect(rect):
        print(cache.name)

If you want to search in a larger area, you could use the ``limit`` parameter as described above.

Load trackable details
---------------------------------------------------------------------------------------------------

.. code-block:: python

    trackable = geocaching.get_trackable("TB3ZGT2")
    print(trackable.name, trackable.goal, trackable.description, trackable.location)


Post a log for trackable
---------------------------------------------------------------------------------------------------

.. code-block:: python

    from pycaching.log import Log, Type as LogType
    import datetime

    log = Log(type=LogType.discovered_it, text="Nice TB!", visited=datetime.date.today())
    tracking_code = "ABCDEF"
    trackable.post_log(log, tracking_code)

Get geocaches by log type
---------------------------------------------------------------------------------------------------

.. code-block:: python

    from pycaching.log import Type as LogType

    for find in geocaching.my_finds(limit=5):
        print(find.name)

    for dnf in geocaching.my_dnfs(limit=2):
        print(dnf.name)

    for note in geocaching.my_logs(LogType.note, limit=6):
        print(note.name)


.. _appendix:

Appendix
===================================================================================================

Legal notice
---------------------------------------------------------------------------------------------------

Be sure to read `Geocaching.com's terms of use <http://www.geocaching.com/about/termsofuse.aspx>`__.
By using this piece of software you break them and your Geocaching account may be suspended or *even
deleted*. To prevent this, I recommend you to load the data you really need, nothing more. This
software is provided "as is" and I am not responsible for any damage possibly caused by it.

Inspiration
---------------------------------------------------------------------------------------------------

Original version was inspired by these packages:

-  `Geocache Grabber <http://www.cs.auckland.ac.nz/~fuad/geo.py>`__ (by Fuad Tabba)
-  `geocaching-py <https://github.com/abbot/geocaching-py>`__ (by Lev Shamardin)

Although the new version was massively rewritten, I'd like to thank to their authors.

Authors
---------------------------------------------------------------------------------------------------

Authors of this project are `all contributors
<https://github.com/tomasbedrich/pycaching/graphs/contributors>`__. Maintainer is `Tomáš Bedřich
<http://tbedrich.cz>`__.

.. _build_status:

|PyPI monthly downloads|

.. |PyPI monthly downloads| image:: http://img.shields.io/pypi/dm/pycaching.svg
   :target: https://pypi.python.org/pypi/pycaching
