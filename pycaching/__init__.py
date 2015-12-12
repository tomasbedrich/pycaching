#!/usr/bin/env python3

from pycaching.cache import Cache  # NOQA
from pycaching.geocaching import Geocaching  # NOQA
from pycaching.log import Log  # NOQA
from pycaching.trackable import Trackable  # NOQA
from pycaching.geo import Point, Rectangle  # NOQA


def login(username=None, password=None):
    """A shortcut for user login.

    Create a :class:`.Geocaching` instance and try to login a user. See :meth:`.Geocaching.login`.

    :return: Created :class:`.Geocaching` instance.
    """
    g = Geocaching()
    g.login(username, password)
    return g
