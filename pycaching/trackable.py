#!/usr/bin/env python3

from pycaching import errors
from pycaching.log import Log
from pycaching.log import Type as LogType
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
        release_date=None,
        last_logs=None
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
        if release_date is not None:
            self.release_date = release_date
        if last_logs is not None:
            self.last_logs = last_logs
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
        """The trackable origin as shown on its details page.

        Either a country (eg. "Germany") or a state and a country (eg. "Bayern, Germany").
        Empty string if the origin is unknown.

        :type: :class:`str`
        """
        return self._origin

    @origin.setter
    def origin(self, origin):
        self._origin = origin.strip()

    @property
    @lazy_loaded
    def origin_country(self):
        """The country part of the trackable :attr:`origin`.

        :type: :class:`str`
        """
        if "," in self._origin:  # there is a state and a country
            return self._origin.rsplit(", ", 1)[1]
        else:  # only country or no value
            return self._origin

    @property
    @lazy_loaded
    def origin_state(self):
        """The state part of the trackable :attr:`origin`, empty string if there is none.

        :type: :class:`str`
        """
        if "," in self._origin:  # there is a state and a country
            return self._origin.rsplit(", ", 1)[0]
        else:  # only country or no value
            return ""

    @property
    @lazy_loaded
    def release_date(self):
        """The trackable release date.

        :setter: Set a release date. If :class:`str` is passed, then :meth:`.util.parse_date`
            is used and its return value is stored. Empty string if the date is missing or
            cannot be parsed.
        :type: :class:`datetime.date` or :class:`str`
        """
        return self._release_date

    @release_date.setter
    def release_date(self, release_date):
        if release_date is not None:
            try:
                self._release_date = parse_date(release_date)
            except Exception:
                self._release_date = ""
        else:
            self._release_date = ""

    @property
    @lazy_loaded
    def last_logs(self):
        """The latest logs shown on the trackable details page (up to 10), newest first.

        :type: :class:`list` of :class:`.Log`
        """
        return self._last_logs

    @last_logs.setter
    def last_logs(self, last_logs):
        self._last_logs = last_logs

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
        # some elements are missing on the pages of inactive trackables
        owner = root.find(id="ctl00_ContentBody_BugDetails_BugOwner")
        self.owner = owner.text if owner else ""
        goal = root.find(id="TrackableGoal")
        self.goal = goal.text if goal else ""
        description = root.find(id="TrackableDetails")
        self.description = description.text if description else ""
        origin = root.find(id="ctl00_ContentBody_BugDetails_BugOrigin")
        self.origin = origin.text if origin else ""
        release_date = root.find(id="ctl00_ContentBody_BugDetails_BugReleaseDate")
        self.release_date = release_date.text if release_date else None

        kml_link = root.find(id="ctl00_ContentBody_lnkGoogleKML")
        if kml_link:
            self._kml_url = kml_link.get("href")

        # another Groundspeak trick... inconsistent relative / absolute URL on one page
        log_link = root.find(id="ctl00_ContentBody_LogLink")
        if log_link:
            self._log_page_url = "/track/" + log_link["href"]

        location_raw = root.find(id="ctl00_ContentBody_BugDetails_BugLocation")
        if location_raw is None:
            self.location = ""
        elif "cache_details" in location_raw.get("href", ""):
            self.location = location_raw.get("href")
        else:
            self.location = location_raw.text

        self.last_logs = self._get_logs_from_details_page(root)

    @staticmethod
    def _get_logs_from_details_page(soup):
        """Return a list of the latest logs shown on the trackable details page.

        The details page shows only the most recent logs (up to 10), so this is not a complete
        log history of the trackable.

        :param bs4.BeautifulSoup soup: Parsed html document of the trackable details page.
        :rtype: :class:`list` of :class:`.Log`
        """
        table = soup.find("table", "TrackableItemLogTable")
        if table is None:  # no logs, e.g. for inactive trackables
            return []

        logs = []
        # every log consists of two rows: a header row with the metadata and a row with the log text
        for header_row in table.find_all("tr", "BorderTop"):
            header = header_row.find("th")
            type_filename = header.img["src"].split("/")[-1].split(".")[0]  # "/images/logtypes/48.png" -> "48"
            author_cell, _, link_cell = header_row.find_all("td")[:3]
            log_url = link_cell.a["href"]  # ".../track/log.aspx?LUID=<uuid>"

            text_row = header_row.find_next_sibling("tr", "BorderBottom")
            text = text_row.find("div", "TrackLogText") if text_row else None

            logs.append(
                Log(
                    uuid=log_url.split("LUID=")[-1].strip(),
                    type=LogType.from_filename(type_filename),
                    text=text.get_text() if text else "",
                    visited=header.get_text().strip(),
                    author=author_cell.a.get_text(),
                )
            )
        return logs

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
