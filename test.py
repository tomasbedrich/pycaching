#!/usr/bin/env python3

import logging
import pycaching
from pycaching import Point, Rectangle

logging.basicConfig(level=logging.DEBUG)

_username, _password = "cache-map", "pGUgNw59"
g = pycaching.login(_username, _password)

a = Rectangle(Point.from_location(g, "Namesti Republiky, Pilsen, Czech Republic"), Point.from_location(g, "Sady petatricatniku, Pilsen, Czech Republic"))

for c in g.search_quick(a, 100):
    print("{:<8} | {:<50} | {:<40} | {:.3}m".format(c.wp, c.name, c.location, c.location.precision))
