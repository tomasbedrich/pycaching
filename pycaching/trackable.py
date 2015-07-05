#!/usr/bin/env python3

import logging
import datetime
from pycaching.errors import ValueError
from pycaching.errors import LoadError
from pycaching.point import Point
from pycaching.util import Util


def lazy_loaded(func):
    """Decorator providing lazy loading."""

    def wrapper(*args, **kwargs):
        self = args[0]
        assert isinstance(self, Trackable)
        try:
            return func(*args, **kwargs)
        except AttributeError:
            logging.debug("Lazy loading: %s", func.__name__)
            if hasattr(self, 'trackable_page'):
                self.geocaching.load_trackable_by_url(self.trackable_page, self)
            elif hasattr(self, '_tid'):
                self.geocaching.load_trackable(self.tid, self)
            else:
                raise LoadError("Trackable lacks info for lazy loading")

            return func(*args, **kwargs)

    return wrapper


class Trackable(object):

    def __init__(self, tid, geocaching, *, name=None, location=None, owner=None,
                 type=None, description=None, goal=None, trackable_page=None):
        if geocaching is not None:
           self.geocaching = geocaching
        else:
            raise ValueError
        if tid is not None:
           self.tid = tid # Tracking ID
        if name is not None:
           self.name = name
        if location is not None:
           self.location = location
        if owner is not None:
           self.owner = owner
        if description is not None:
            self.desctiption = description
        if goal is not None:
            self.goal = goal
        if type is not None:
            self.type = type
        if description is not None:
            self.description = description
        if trackable_page is not None:
            self.trackable_page = trackable_page

    def __str__(self):
        return self.tid

    def __eq__(self, other):
        return self.tid == other.tid

    @property
    @lazy_loaded
    def tid(self):
        return self._tid

    @tid.setter
    def tid(self, tid):
        tid = str(tid).upper().strip()
        if not tid.startswith("TB"):
            raise ValueError("Trackable ID '{}' doesn't start with 'TB'.".format(tid))
        self._tid = tid

    @property
    def geocaching(self):
        return self._geocaching

    @geocaching.setter
    def geocaching(self, geocaching):
        if not hasattr(geocaching, "load_trackable"):
            raise ValueError("Passed object (type: '{}') doesn't contain 'load_trackable' method.".format(type(geocaching)))
        self._geocaching = geocaching

    @property
    @lazy_loaded
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        name = str(name).strip()
        self._name = name

    @property
    @lazy_loaded
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    @lazy_loaded
    def goal(self):
        return self._goal

    @goal.setter
    def goal(self, goal):
        self._goal = goal.strip()

    @property
    @lazy_loaded
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc.strip()

    @property
    @lazy_loaded
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner.strip()

    @property
    @lazy_loaded
    def type(self):
        return self._type

    @type.setter
    def type(self, trackable_type):
        self._type = trackable_type.strip()
