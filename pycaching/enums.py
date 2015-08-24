#!/usr/bin/env python3

from pycaching.errors import ValueError as PycachingValueError
from enum import Enum


class Type(Enum):

    # value is cache image filename (http://www.geocaching.com/images/WptTypes/[VALUE].gif)
    traditional = "2"
    multicache = "3"
    mystery = unknown = "8"
    letterbox = "5"
    event = "6"
    mega_event = "mega"
    giga_event = "giga"
    earthcache = "137"
    cito = cache_in_trash_out_event = "13"
    webcam = "11"
    virtual = "4"
    wherigo = "1858"
    lost_and_found_event = "10Years_32"
    project_ape = "ape_32"
    groundspeak_hq = "HQ_32"
    gps_adventures_exhibit = "1304"
    groundspeak_block_party = "4738"
    locationless = reverse = "12"

    @classmethod
    def from_filename(cls, filename):
        """Returns cache type from its image filename"""

        if filename == "earthcache":
            filename = "137"  # fuck Groundspeak, they use 2 exactly same icons with 2 different names

        return cls(filename)

    @classmethod
    def from_string(cls, name):
        """Returns cache type from its human readable name"""

        name = name.replace(" Geocache", "")  # with space!
        name = name.replace(" Cache", "")  # with space!
        name = name.lower().strip()

        name_mapping = {
            "traditional": cls.traditional,
            "multi-cache": cls.multicache,
            "mystery": cls.mystery,
            "unknown": cls.unknown,
            "letterbox hybrid": cls.letterbox,
            "event": cls.event,
            "mega-event": cls.mega_event,
            "giga-event": cls.giga_event,
            "earthcache": cls.earthcache,
            "cito": cls.cito,
            "cache in trash out event": cls.cache_in_trash_out_event,
            "webcam": cls.webcam,
            "virtual": cls.virtual,
            "wherigo": cls.wherigo,
            "lost and found event": cls.lost_and_found_event,
            "project ape": cls.project_ape,
            "groundspeak hq": cls.groundspeak_hq,
            "gps adventures exhibit": cls.gps_adventures_exhibit,
            "groundspeak block party": cls.groundspeak_block_party,
            "locationless (reverse)": cls.locationless,
        }

        try:
            return name_mapping[name]
        except KeyError as e:
            raise PycachingValueError("Unknown cache type '{}'.".format(name)) from e


class Size(Enum):
    micro = "micro"
    small = "small"
    regular = "regular"
    large = "large"
    not_chosen = "not chosen"
    virtual = "virtual"
    other = "other"

    @classmethod
    def from_filename(cls, filename):
        """Returns cache size from its image filename"""
        return cls[filename]

    @classmethod
    def from_string(cls, name):
        """Returns cache size from its human readable name"""
        name = name.strip().lower()

        try:
            return cls(name)
        except ValueError as e:
            raise PycachingValueError("Unknown cache type '{}'.".format(name)) from e


class LogType(Enum):
    found_it = "found it"
    didnt_find_it = "didn't find it"
    note = "write note"
    publish_listing = "publish listing"
    enable_listing = "enable listing"
    archive = "archive"
    unarchive = "unarchive"
    temp_disable_listing = "temporarily disable listing"
    needs_archive = "needs archived"
    will_attend = "will attend"
    attended = "attended"
    retrieved_it = "retrieved it"
    placed_it = "placed it"
    grabbed_it = "grabbed it"
    needs_maintenance = "needs maintenance"
    owner_maintenance = "owner maintenance"
    update_coordinates = "update coordinates"
    discovered_it = "discovered it"
    post_reviewer_note = "post reviewer note"
    submit_for_review = "submit for review"
    visit = "visit"
    webcam_photo_taken = "webcam photo taken"
    announcement = "announcement"
    retract = "retract listing"
    marked_missing = "marked missing"
    oc_team_comment = "X1"

    @classmethod
    def from_string(cls, name):
        """Returns log type from its human readable name"""
        name = name.strip().lower()

        try:
            return cls(name)
        except ValueError as e:
            raise PycachingValueError("Unknown log type '{}'.".format(name)) from e
