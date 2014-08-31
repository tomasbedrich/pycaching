#!/usr/bin/env python3


class Error(Exception):
    pass


class NotLoggedInException(Error):
    pass


class LoginFailedException(Error, ValueError):
    pass


class GeocodeError(Error, ValueError):
    pass


class LoadError(Error, OSError):
    pass


class PMOnlyException(Error):
    pass


class ValueError(Error, ValueError):
    pass
