#!/usr/bin/env python3

from pycaching import errors
from pycaching.util import lazy_loaded

# prefix _type() function to avoid colisions with trackable type
_type = type


class Trackable(object):
    """Represents a trackable with its properties."""

    def __init__(self, geocaching, tid, *, name=None, location=None, owner=None,
                 type=None, description=None, goal=None, url=None):
        self.geocaching = geocaching
        if tid is not None:
            self.tid = tid
        if name is not None:
            self.name = name
        if location is not None:
            self.location = location
        if owner is not None:
            self.owner = owner
        if description is not None:
            self.description = description
        if goal is not None:
            self.goal = goal
        if type is not None:
            self.type = type
        if url is not None:
            self.url = url

    def __str__(self):
        """Return trackable ID."""
        return self.tid

    def __eq__(self, other):
        """Compare trackables by their ID."""
        return self.tid == other.tid

    @property
    @lazy_loaded
    def tid(self):
        """The trackable ID, must start with :code:`TB`.

        :type: :class:`str`
        """
        return self._tid

    @tid.setter
    def tid(self, tid):
        tid = str(tid).upper().strip()
        if not tid.startswith("TB"):
            raise errors.ValueError("Trackable ID '{}' doesn't start with 'TB'.".format(tid))
        self._tid = tid

    @property
    def geocaching(self):
        """A reference to :class:`.Geocaching` used for communicating with geocaching.com.

        :type: :class:`.Geocaching` instance
        """
        return self._geocaching

    @geocaching.setter
    def geocaching(self, geocaching):
        if not hasattr(geocaching, "_request"):
            raise errors.ValueError(
                "Passed object (type: '{}') doesn't contain '_request' method.".format(_type(geocaching)))
        self._geocaching = geocaching

    @property
    @lazy_loaded
    def name(self):
        """A human readable trackable name.

        :type: :class:`str`
        """
        return self._name

    @name.setter
    def name(self, name):
        name = str(name).strip()
        self._name = name

    @property
    @lazy_loaded
    def location(self):
        """The trackable current location.

        Can be either string with location description (eg. "in the hands of someone") or cache URL.

        :type: :class:`str`
        """
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    @lazy_loaded
    def goal(self):
        """The trackable goal.

        :type: :class:`str`
        """
        return self._goal

    @goal.setter
    def goal(self, goal):
        self._goal = goal.strip()

    @property
    @lazy_loaded
    def description(self):
        """The trackable long description.

        :type: :class:`str`
        """
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc.strip()

    @property
    @lazy_loaded
    def owner(self):
        """The trackable owner.

        :type: :class:`str`
        """
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner.strip()

    @property
    @lazy_loaded
    def type(self):
        """The trackable type.

        A type depends on the trackable icon. It can be either "Travel Bug Dog Tag" or specific
            geocoin name, eg. "Adventure Race Hracholusky 2015 Geocoin".

        :type: :class:`str`
        """
        return self._type

    @type.setter
    def type(self, type):
        self._type = type.strip()

    def load(self):
        """Load all possible details about the trackable.

        .. note::
           This method is called automatically when you access a property which isn't yet filled in
           (so-called "lazy loading"). You don't have to call it explicitly.

        :raise .LoadError: If trackable loading fails (probably because of not existing cache).
        """
        # pick url based on what info we have right now
        if hasattr(self, "url"):
            url = self.url
        elif hasattr(self, "_tid"):
            url = "track/details.aspx?tracker={}".format(self._tid)
        else:
            raise errors.LoadError("Trackable lacks info for loading")

        # make request
        root = self.geocaching._request(url)

        # parse data
        self.tid = root.find("span", "CoordInfoCode").text
        self.name = root.find(id="ctl00_ContentBody_lbHeading").text
        self.type = root.find(id="ctl00_ContentBody_BugTypeImage").get("alt")
        self.owner = root.find(id="ctl00_ContentBody_BugDetails_BugOwner").text
        self.goal = root.find(id="TrackableGoal").text
        self.description = root.find(id="TrackableDetails").text

        location_raw = root.find(id="ctl00_ContentBody_BugDetails_BugLocation")
        location_url = location_raw.get("href")
        if "cache_details" in location_url:
            self.location = location_url
        else:
            self.location = location_raw.text
