#!/usr/bin/env python3

__title__ = "pycaching"
__version__ = "3.0.dev"  # PEP 386
__author__ = "Tomas Bedrich"
__license__ = "LGPL v3.0"
__copyright__ = "Copyright 2014 Tomas Bedrich"


__all__ = ["geocaching", "cache", "util", "point"]

try:
    from .geocaching import Geocaching  # NOQA
    from .cache import Cache  # NOQA
    from .util import Util  # NOQA
    from .point import Point  # NOQA

except ImportError:  # pragma: no cover
    # ignore when someone is importing this file just to get __magic__
    pass


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
