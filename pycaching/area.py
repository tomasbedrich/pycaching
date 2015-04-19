#!/usr/bin/env python3

from pycaching.point import Point


class Area:
    """Geometrical area"""
    pass


class Polygon(Area):
    """Area defined by bordering Point instances"""

    def __init__(self, *points):
        """Define polygon by list of consecutive Points"""
        assert len(points) >= 3
        self.points = points

    @property
    def bounding_box(self):
        """Get extreme latitude and longitude values.

        Return Rectangle that contains all points"""

        lats = sorted([p.latitude for p in self.points])
        lons = sorted([p.longitude for p in self.points])
        return Rectangle(Point(min(lats), min(lons)),
                         Point(max(lats), max(lons)))

    @property
    def mean_point(self):
        """Return point with average latitude and longitude of points"""
        lats = [p.latitude for p in self.points]
        lons = [p.longitude for p in self.points]
        return Point(sum(lats) / len(lats), sum(lons) / len(lons))

    @property
    def diagonal(self):
        """Return bounding box diagonal"""
        return self.bounding_box.diagonal


class Rectangle(Polygon):
    """Upright rectangle"""

    def __init__(self, point_a, point_b):
        """Create rectangle defined by opposite corners

        Parameters point_a and point_b are Point instances."""

        assert point_a != point_b, "Corner points cannot be the same"
        self.corners = [point_a, point_b]
        self.points = [point_a, Point(point_a.latitude, point_b.longitude),
                       point_b, Point(point_b.latitude, point_a.longitude)]

    def inside_area(self, point):
        """Is point inside area?"""
        lats = sorted([p.latitude for p in self.points])
        lons = sorted([p.longitude for p in self.points])
        if min(lats) <= point.latitude <= max(lats):
            if min(lons) <= point.longitude <= max(lons):
                return True
        return False

    @property
    def diagonal(self):
        """Return rectangle diagonal"""
        return self.corners[0].distance(self.corners[1])
