===============================================================================
API reference
===============================================================================

Here you can find an overview of all available classes and methods.

.. warning::
   Deprecated methods will be removed in next minor version.

   For example: if you rely on some non-deprecated method in version 3.3, then it's fine to update
   once to 3.4. If the method gets deprecated in 3.4, then it will be removed in 3.5!

.. automodule:: pycaching
  :members: login


Geocaching
-------------------------------------------------------------------------------

.. automodule:: pycaching.geocaching
   :members:


Cache
-------------------------------------------------------------------------------

.. autoclass:: pycaching.cache.Cache
   :members:

.. autoclass:: pycaching.cache.Waypoint
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: pycaching.cache.Type
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: pycaching.cache.Size
   :members:
   :undoc-members:
   :inherited-members:


Logs
-------------------------------------------------------------------------------

.. autoclass:: pycaching.log.Log
   :members:

.. autoclass:: pycaching.log.Type
   :members:
   :undoc-members:
   :inherited-members:


Trackables
-------------------------------------------------------------------------------

.. automodule:: pycaching.trackable
   :members:


Geo utilities
-------------------------------------------------------------------------------

.. automodule:: pycaching.geo
   :members: to_decimal

.. autoclass:: pycaching.geo.Point
   :members: from_location, from_string

.. autoclass:: pycaching.geo.Polygon
   :members: bounding_box, mean_point

.. autoclass:: pycaching.geo.Rectangle
   :members: __contains__, diagonal


Errors
-------------------------------------------------------------------------------

.. automodule:: pycaching.errors
   :members:
