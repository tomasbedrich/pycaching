#!/usr/bin/env python3

import logging
import datetime

from .point import Point


def lazy_loaded(func):
    """Decorator providing lazy loading."""

    def wrapper(*args, **kwargs):
        self = args[0]
        assert isinstance(self, Cache)
        try:
            return func(*args, **kwargs)
        except AttributeError:
            logging.debug("Lazy loading: %s", func.__name__)
            self.geocaching.load_cache(self.wp, self)
            return func(*args, **kwargs)

    return wrapper


class Cache(object):

    # attributes will probably require some maintenance
    # TODO: generate from http://opencaching-api.googlecode.com/svn/trunk/okapi/services/attrs/attribute-definitions.xml
    # TODO: or better parse from http://www.geocaching.com/about/icons.aspx
    _possible_attributes = {
        "dog": "Dogs",
        "dogs": "Dogs allowed",
        "fee": "Access or parking fee",
        "rappelling": "Climbing gear",
        "boat": "Boat",
        "scuba": "Scuba gear",
        "kids": "Recommended for kids",
        "onehour": "Takes less than an hour",
        "scenic": "Scenic view",
        "hike_short": "Short hike (less than 1km)",
        "hike_med": "Medium hike (1km - 10km)",
        "hike_long": "Long hike (+10km)",
        "hiking": "Significant hike",
        "climbing": "Difficult climbing",
        "wading": "May require wading",
        "swimming": "May require swimming",
        "available": "Available at all times",
        "night": "Recommended at night",
        "winter": "Available during winter",
        "poisonoak": "Poison plants",
        "snakes": "Snakes",
        "ticks": "Ticks",
        "mines": "Abandoned mines",
        "cliff": "Cliff / falling rocks",
        "hunting": "Hunting",
        "danger": "Dangerous area",
        "wheelchair": "Wheelchair accessible",
        "parkngrab": "Park and grab",
        "parking": "Parking available",
        "public": "Public transportation",
        "water": "Drinking water nearby",
        "restrooms": "Public restrooms nearby",
        "phone": "Telephone nearby",
        "picnic": "Picnic tables nearby",
        "camping": "Camping available",
        "bicycles": "Bicycles",
        "motorcycles": "Motorcycles",
        "quads": "Quads",
        "jeeps": "Off-road vehicles",
        "snowmobiles": "Snowmobiles",
        "horses": "Horses",
        "campfires": "Campfires",
        "thorns": "Thorns",
        "thorn": "Thorns!",
        "stealth": "Stealth required",
        "stroller": "Stroller accessible",
        "firstaid": "Needs maintenance",
        "cow": "Watch for livestock",
        "flashlight": "Flashlight required",
        "landf": "Lost And Found Tour",
        "s-tool": "Special tool required",
        "field_puzzle": "Is field puzzle",
        "treeclimbing": "Tree climbing required",
    }

    _possible_types = {
        "Traditional Cache",
        "Multi-Cache",
        "Unknown Cache",
        "Mystery Cache",
        "Letterbox Hybrid",
        "Event Cache",
        "Mega-Event Cache",
        "Giga-Event Cache",
        "Earthcache",
        "Cache In Trash Out Event",
        "Webcam Cache",
        "Virtual Cache",
        "Wherigo Cache",
        "Lost And Found Event Cache",
        "Project Ape Cache",
        "Groundspeak Hq",
        "Gps Adventures Exhibit",
        "Groundspeak Block Party",
        "Locationless (Reverse) Cache",
    }

    _possible_sizes = {
        "nano",
        "micro",
        "small",
        "regular",
        "large",
        "very large",
        "not chosen",
        "virtual",
        "other"
    }

    def __init__(self, wp, geocaching, *, name=None, cache_type=None, location=None, state=None,
                 found=None, size=None, difficulty=None, terrain=None, author=None, hidden=None,
                 attributes=None, summary=None, description=None, hint=None, favorites=None, pm_only=None):
        self.wp = wp
        self.geocaching = geocaching
        if name is not None:
            self.name = name
        if cache_type is not None:
            self.cache_type = cache_type
        if location is not None:
            self.location = location
        if state is not None:
            self.state = state
        if found is not None:
            self.found = found
        if size is not None:
            self.size = size
        if difficulty is not None:
            self.difficulty = difficulty
        if terrain is not None:
            self.terrain = terrain
        if author is not None:
            self.author = author
        if hidden is not None:
            self.hidden = hidden
        if attributes is not None:
            self.attributes = attributes
        if summary is not None:
            self.summary = summary
        if description is not None:
            self.description = description
        if hint is not None:
            self.hint = hint
        if favorites is not None:
            self.favorites = favorites
        if pm_only is not None:
            self.pm_only = pm_only

    def __str__(self):
        return self.wp

    def __eq__(self, other):
        return self.wp == other.wp

    @property
    def wp(self):
        return self._wp

    @wp.setter
    def wp(self, wp):
        assert type(wp) is str
        wp = wp.upper().strip()
        assert wp.startswith("GC")
        self._wp = wp

    @property
    def geocaching(self):
        return self._geocaching

    @geocaching.setter
    def geocaching(self, geocaching):
        from .geocaching import Geocaching
        assert isinstance(geocaching, Geocaching)
        self._geocaching = geocaching

    @property
    @lazy_loaded
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        assert type(name) is str
        name = name.strip()
        self._name = name

    @property
    @lazy_loaded
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        assert type(location) is Point
        self._location = location

    @property
    @lazy_loaded
    def cache_type(self):
        return self._cache_type

    @cache_type.setter
    def cache_type(self, cache_type):
        cache_type = cache_type.strip().title()
        cache_type = cache_type.replace("Geocache", "Cache")
        assert cache_type in self._possible_types
        self._cache_type = cache_type

    @property
    @lazy_loaded
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        assert type(state) is bool
        self._state = state

    @property
    @lazy_loaded
    def found(self):
        return self._found

    @found.setter
    def found(self, found):
        assert type(found) is bool
        self._found = found

    @property
    @lazy_loaded
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        size = size.strip().lower()
        assert size in self._possible_sizes
        self._size = size

    @property
    @lazy_loaded
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        assert type(difficulty) in (int, float)
        assert difficulty >= 1 and difficulty <= 5
        assert difficulty * 10 % 5 == 0  # X.0 or X.5
        self._difficulty = difficulty

    @property
    @lazy_loaded
    def terrain(self):
        return self._terrain

    @terrain.setter
    def terrain(self, terrain):
        assert type(terrain) in (int, float)
        assert terrain >= 1 and terrain <= 5
        assert terrain * 10 % 5 == 0  # X.0 or X.5
        self._terrain = terrain

    @property
    @lazy_loaded
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        assert type(author) is str
        author = author.strip()
        self._author = author

    @property
    @lazy_loaded
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        assert type(hidden) is datetime.date
        self._hidden = hidden

    @property
    @lazy_loaded
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        assert type(attributes) is dict

        self._attributes = {}
        for name, allowed in attributes.items():
            name = name.strip()
            if name in self._possible_attributes:
                self._attributes[name] = allowed
            else:
                logging.warning("Unknown attribute '%s', ignoring.", name)

    @property
    @lazy_loaded
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        assert type(summary) is str
        summary = summary.strip()
        self._summary = summary

    @property
    @lazy_loaded
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        assert type(description) is str
        description = description.strip()
        self._description = description

    @property
    @lazy_loaded
    def hint(self):
        return self._hint

    @hint.setter
    def hint(self, hint):
        assert type(hint) is str
        hint = hint.strip()
        self._hint = hint

    @property
    @lazy_loaded
    def favorites(self):
        return self._favorites

    @favorites.setter
    def favorites(self, favorites):
        assert type(favorites) is int
        self._favorites = favorites

    @property
    def pm_only(self):
        return self._pm_only

    @pm_only.setter
    def pm_only(self, pm_only):
        assert type(pm_only) is bool
        self._pm_only = pm_only
