#!/usr/bin/env python3

import logging
import datetime
import geopy as geo


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
        "Multi-cache",
        "Unknown Cache",
        "Mystery Cache",
        "Letterbox hybrid",
        "Event Cache",
        "Mega-Event Cache",
        "Giga-Event Cache",
        "Earthcache",
        "Cache in Trash out Event",
        "Webcam Cache",
        "Virtual Cache",
        "Wherigo Cache",
        "Lost and Found Event Cache",
        "Project Ape Cache",
        "Groundspeak HQ",
        "GPS Adventures Exhibit",
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

    def __init__(self, wp, name=None, cacheType=None, location=None, state=None,
                 found=None, size=None, difficulty=None, terrain=None, author=None, hidden=None,
                 attributes=None, summary=None, description=None, hint=None, favorites=None):
        self.wp = wp
        if name:
            self.name = name
        if cacheType:
            self.cacheType = cacheType
        if location:
            self.location = location
        if state:
            self.state = state
        if found:
            self.found = found
        if size:
            self.size = size
        if difficulty:
            self.difficulty = difficulty
        if terrain:
            self.terrain = terrain
        if author:
            self.author = author
        if hidden:
            self.hidden = hidden
        if attributes:
            self.attributes = attributes
        if summary:
            self.summary = summary
        if description:
            self.description = description
        if hint:
            self.hint = hint
        if favorites:
            self.favorites = favorites

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
        assert wp.startswith("GC")
        self._wp = wp

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        assert type(name) is str
        self._name = name

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        assert type(location) is geo.Point
        self._location = location

    @property
    def cacheType(self):
        return self._cacheType

    @cacheType.setter
    def cacheType(self, cacheType):
        assert cacheType in self._possible_types
        self._cacheType = cacheType

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        assert type(state) is bool
        self._state = state

    @property
    def found(self):
        return self._found

    @found.setter
    def found(self, found):
        assert type(found) is bool
        self._found = found

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        assert size in self._possible_sizes
        self._size = size

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        assert type(difficulty) in (int, float)
        assert difficulty >= 1 and difficulty <= 5
        assert difficulty * 10 % 5 == 0  # X.0 or X.5
        self._difficulty = difficulty

    @property
    def terrain(self):
        return self._terrain

    @terrain.setter
    def terrain(self, terrain):
        assert type(terrain) in (int, float)
        assert terrain >= 1 and terrain <= 5
        assert terrain * 10 % 5 == 0  # X.0 or X.5
        self._terrain = terrain

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        assert type(author) is str
        self._author = author

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        assert type(hidden) is datetime.date
        self._hidden = hidden

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        assert type(attributes) is dict

        self._attributes = {}
        for name, allowed in attributes.items():
            if name in self._possible_attributes:
                self._attributes[name] = allowed
            else:
                logging.warning("Unknown attribute '%s', ignoring.", name)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        assert type(summary) is str
        self._summary = summary

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        assert type(description) is str
        self._description = description

    @property
    def hint(self):
        return self._hint

    @hint.setter
    def hint(self, hint):
        assert type(hint) is str
        self._hint = hint

    @property
    def favorites(self):
        return self._favorites

    @favorites.setter
    def favorites(self, favorites):
        assert type(favorites) is int
        self._favorites = favorites
