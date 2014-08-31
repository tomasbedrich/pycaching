#!/usr/bin/env python3

__title__ = "pycaching"
__version__ = "3.0.dev"  # PEP 386
__author__ = "Tomas Bedrich"
__license__ = "LGPL v3.0"
__copyright__ = "Copyright 2014 Tomas Bedrich"


__all__ = ["geocaching", "cache", "util", "point"]


from pycaching.geocaching import Geocaching  # NOQA
from pycaching.cache import Cache  # NOQA
from pycaching.util import Util  # NOQA
from pycaching.point import Point  # NOQA


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
