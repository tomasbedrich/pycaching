#!/usr/bin/env python3

from bs4 import BeautifulSoup

from pycaching import errors
from pycaching.log import Log
from pycaching.util import format_date, lazy_loaded, parse_date

# prefix _type() function to avoid collisions with trackable type
_type = type


class Trackable(object):
    """Represents a trackable with its properties."""

    def __init__(
        self,
        geocaching,
        tid,
        *,
        name=None,
        location=None,
        owner=None,
        type=None,
        description=None,
        goal=None,
        url=None,
        origin=None,
        releaseDate=None,
        lastTBLogs=None
    ):
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
        if origin is not None:
            self.origin = origin
        if releaseDate is not None:
            self.releaseDate = releaseDate
        if lastTBLogs is not None:
            self.lastTBLogs = lastTBLogs
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
                "Passed object (type: '{}') doesn't contain '_request' method.".format(_type(geocaching))
            )
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
        if location is not None:
            location = location.strip()
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
    def type(self, type_):
        if type_ is not None:
            type_ = type_.strip()
        self._type = type_

    def get_KML(self):
        """Return the KML route of the trackable.

        :rtype: :class:`str`
        """
        if not self._kml_url:
            self.load()  # fills self._kml_url
        return self.geocaching._request(self._kml_url, expect="raw").text

    @property
    @lazy_loaded
    def origin(self):
        """The trackable origin.

        :type: :class:`str`
        """
        return self._origin

    @origin.setter
    def origin(self, origin):
        self._origin = origin.strip()

    @property
    @lazy_loaded
    def originCountry(self):
        """The trackable origin country.

        :type: :class:`str`
        """
        if "," in self._origin:  # there is a state and a country
            return self._origin.rsplit(", ", 1)[1]
        else:  # only country or no value
            return self._origin

    @property
    @lazy_loaded
    def originState(self):
        """The trackable origin state.

        :type: :class:`str`
        """
        if "," in self._origin:  # there is a state and a country
            return self._origin.rsplit(", ", 1)[0]
        else:  # only country or no value
            return ""

    @property
    @lazy_loaded
    def releaseDate(self):
        """The trackable releaseDate.

        :type: :class:`str`
        """
        return self._releaseDate

    @releaseDate.setter
    def releaseDate(self, releaseDate):
        if releaseDate is not None:
            try:
                self._releaseDate = parse_date(releaseDate)
            except Exception:
                self._releaseDate = ""
        else:
            self._releaseDate = ""

    @property
    @lazy_loaded
    def lastTBLogs(self):
        """The trackable lastLogs.

        :type: :class:`str`
        """
        return self._lastTBLogs

    @lastTBLogs.setter
    def lastTBLogs(self, lastTBLogs):
        self._lastTBLogs = lastTBLogs

    def load(self):
        """Load all possible details about the trackable.

        .. note::
           This method is called automatically when you access a property which isn't yet filled in
           (so-called "lazy loading"). You don't have to call it explicitly.

        :raise .LoadError: If trackable loading fails (probably because of not existing trackable).
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
        bugDetails = root.find(id="ctl00_ContentBody_BugDetails_BugOwner")
        if bugDetails is not None:
            self.owner = root.find(id="ctl00_ContentBody_BugDetails_BugOwner").text
        else:
            self.owner = ""
        tbGoal = root.find(id="TrackableGoal")
        if tbGoal is not None:
            self.goal = root.find(id="TrackableGoal").text
        else:
            self.goal = ""
        tbDescription = root.find(id="TrackableDetails")
        if tbDescription is not None:
            self.description = root.find(id="TrackableDetails").text
        else:
            self.description = ""
        tbKml = root.find(id="ctl00_ContentBody_lnkGoogleKML")
        if tbKml is not None:
            self._kml_url = root.find(id="ctl00_ContentBody_lnkGoogleKML").get("href")
        bugOrigin = root.find(id="ctl00_ContentBody_BugDetails_BugOrigin")
        if bugOrigin is not None:
            self.origin = root.find(id="ctl00_ContentBody_BugDetails_BugOrigin").text
        else:
            self.origin = ""
        tbReleaseDate = root.find(id="ctl00_ContentBody_BugDetails_BugReleaseDate")
        if tbReleaseDate is not None:
            self.releaseDate = root.find(id="ctl00_ContentBody_BugDetails_BugReleaseDate").text
        else:
            self.releaseDate = ""

        # another Groundspeak trick... inconsistent relative / absolute URL on one page
        logLink = root.find(id="ctl00_ContentBody_LogLink")
        if logLink is not None:
            self._log_page_url = "/track/" + root.find(id="ctl00_ContentBody_LogLink")["href"]

        location_raw = root.find(id="ctl00_ContentBody_BugDetails_BugLocation")
        if location_raw is not None:
            location_url = location_raw.get("href", "")
        else:
            location_url = ""
        if "cache_details" in location_url:
            self.location = location_url
        else:
            if location_raw is not None:
                self.location = location_raw.text
            else:
                self.location = ""

        # Load logs which have been already loaded by that request into log object
        lastTBLogsTmp = []
        soup = BeautifulSoup(str(root), "html.parser")  # Parse the HTML as a string
        table = soup.find("table", {"class": "TrackableItemLogTable Table"})  # Grab log table
        if table is not None:  # handle no logs eg when TB is not active
            for row in table.find_all("tr"):
                if "BorderTop" in row["class"]:
                    header = row.find("th")  # there should only be one
                    tbLogType = header.img["title"]
                    tbLogDate = parse_date(header.get_text().replace("&nbsp", "").strip())
                    tbLogOwnerRow = row.find("td")  # we need the first one
                    tbLogOwner = tbLogOwnerRow.a.get_text().strip()
                    tbLogGUIDRow = row.findAll("td")[2]  # we the third one
                    tbLogGUID = (
                        tbLogGUIDRow.a["href"].strip().replace("https://www.geocaching.com/track/log.aspx?LUID=", "")
                    )
                if "BorderBottom" in row["class"]:
                    logRow = row.find("td")  # there should only be one
                    tbLogText = logRow.div.get_text().strip()
                    # create and fill log object
                    lastTBLogsTmp.append(
                        Log(
                            uuid=tbLogGUID,
                            type=tbLogType,
                            text=tbLogText,
                            visited=tbLogDate,
                            author=tbLogOwner,
                        )
                    )
        self.lastTBLogs = lastTBLogsTmp

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
        date_format = log_page.find(id="ctl00_ContentBody_LogBookPanel1_uxDateFormatHint").text.strip("()")

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
