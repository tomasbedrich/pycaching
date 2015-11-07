#!/usr/bin/env python3

from pycaching.cache import Cache  # NOQA
from pycaching.geocaching import Geocaching  # NOQA
from pycaching.log import Log  # NOQA
from pycaching.trackable import Trackable  # NOQA
from pycaching.geo import Point, Rectangle  # NOQA


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
