#!/usr/bin/env python3

__all__ = ["geocaching", "cache", "util", "point", "errors"]

from .geocaching import Geocaching  # NOQA
from .cache import Cache  # NOQA
from .util import Util  # NOQA
from .point import Point  # NOQA
from .area import Rectangle  # NOQA
from .errors import *  # NOQA


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
