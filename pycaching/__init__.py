#!/usr/bin/env python3

__all__ = ["geocaching", "cache", "util", "point", "errors"]

from pycaching.geocaching import Geocaching  # NOQA
from pycaching.cache import Cache  # NOQA
from pycaching.util import Util  # NOQA
from pycaching.point import Point  # NOQA
from pycaching.area import Rectangle  # NOQA
from pycaching.errors import *  # NOQA


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
