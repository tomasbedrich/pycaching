#!/usr/bin/env python3

from pycaching import errors
from pycaching.util import lazy_loaded, format_date

# prefix _type() function to avoid collisions with trackable type
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
        self._log_page_url = None
        self._kml_url = None

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

    def get_KML(self):
        """Return the KML route of the trackable.

        :rtype: :class:`str`
        """
        if not self._kml_url:
            self.load()  # fills self._kml_url
        return self.geocaching._request(self._kml_url, expect="raw").text

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
        self._kml_url = root.find(id="ctl00_ContentBody_lnkGoogleKML").get("href")

        # another Groundspeak trick... inconsistent relative / absolute URL on one page
        self._log_page_url = "/track/" + root.find(id="ctl00_ContentBody_LogLink")["href"]

        location_raw = root.find(id="ctl00_ContentBody_BugDetails_BugLocation")
        location_url = location_raw.get("href", "")
        if "cache_details" in location_url:
            self.location = location_url
        else:
            self.location = location_raw.text

    def _load_log_page(self):
        """Load a logging page for this trackable.

        :return: Tuple of data necessary to log the trackable.
        :rtype: :class:`tuple` of (:class:`set`:, :class:`dict`, class:`str`)
        """
        if not self._log_page_url:
            self.load()  # fills self._log_page_url
        log_page = self.geocaching._request(self._log_page_url)

        # find all valid log types for the trackable (-1 removes "- select type of log -")
        valid_types = {o["value"] for o in log_page.find_all("option") if o["value"] != "-1"}

        # find all static data fields needed for log
        hidden_inputs = log_page.find_all("input", type=["hidden"])
        hidden_inputs = {i["name"]: i.get("value", "") for i in hidden_inputs}

        # get user date format
        date_format = log_page.find(
            id="ctl00_ContentBody_LogBookPanel1_uxDateFormatHint").text.strip("()")

        return valid_types, hidden_inputs, date_format

    def post_log(self, log, tracking_code):
        """Post a log for this trackable.

        :param .Log log: Previously created :class:`Log` filled with data.
        :param str tracking_code: A tracking code to verify current trackable holder.
        """
        if not log.text:
            raise errors.ValueError("Log text is empty")

        valid_types, hidden_inputs, date_format = self._load_log_page()
        if log.type.value not in valid_types:
            raise errors.ValueError("The trackable does not accept this type of log")

        # assemble post data
        post = hidden_inputs
        formatted_date = format_date(log.visited, date_format)
        post["ctl00$ContentBody$LogBookPanel1$btnSubmitLog"] = "Submit Log Entry"
        post["ctl00$ContentBody$LogBookPanel1$ddLogType"] = log.type.value
        post["ctl00$ContentBody$LogBookPanel1$uxDateVisited"] = formatted_date
        post["ctl00$ContentBody$LogBookPanel1$tbCode"] = tracking_code
        post["ctl00$ContentBody$LogBookPanel1$uxLogInfo"] = log.text

        self.geocaching._request(self._log_page_url, method="POST", data=post)
