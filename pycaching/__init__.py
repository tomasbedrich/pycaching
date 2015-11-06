#!/usr/bin/env python3

from pycaching.area import Rectangle  # NOQA
from pycaching.cache import Cache  # NOQA
from pycaching.geocaching import Geocaching  # NOQA
from pycaching.log import Log  # NOQA
from pycaching.point import Point  # NOQA
from pycaching.trackable import Trackable  # NOQA


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
