#!/usr/bin/env python3


class Error(Exception):
    """General pycaching error.

    .. note:
       This class is a superclass of all errors produced by pycaching module, so you can use it to
       catch all pycaching related errors.
    """
    pass


class NotLoggedInException(Error):
    """Tried to perform an operation which requires logging in first."""
    pass


class LoginFailedException(Error, ValueError):
    """Login failed.

    The provided credentials probably doesn't work to log in.
    """
    pass


class GeocodeError(Error, ValueError):
    """Geocoding failed.

    Probably because of non-existing location.
    """
    pass


class LoadError(Error, OSError):
    """Object loading failed.

    Probably because of non-existing object or missing informations required to load it.
    """
    pass


class PMOnlyException(Error):
    """Requested cache is PM only."""
    pass


class BadBlockError(Error):
    pass


class ValueError(Error, ValueError):
    """Wrapper for Pythons native ValueError.

    Can be raised in various situations, but most commonly when unexpected property value is set.
    """
    pass
